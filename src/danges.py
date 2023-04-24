from duels import *


class Mob:
    def __init__(self, mob_id):
        self.id = mob_id
        mob_info_list = db.get_mob_main_info(mob_id)
        self.name = mob_info_list[0]
        self.health = mob_info_list[1]
        self.attack = mob_info_list[2]
        self.armor_state = mob_info_list[3]
        self.is_bleeding = False
        self.is_stunned = False

    def apply_physical_attack(self, attack: Attack, full_log: list, cur_turn: int) -> None:
        full_damage = attack.physical_dmg
        if attack.is_crit:
            full_damage *= 1.5
        self.is_bleeding = attack.is_bleeding
        self.is_stunned = attack.is_stun
        self.apply_raw_damage(full_damage, attack.has_ignored_armor)

    def apply_raw_damage(self, damage: int, armor_ignored: bool) -> None:
        if armor_ignored:
            self.health -= damage
            pass
        self.armor_state -= damage
        if self.armor_state < 0:
            self.health -= abs(self.armor_state)
            self.armor_state = 0

    def is_dead(self) -> bool:
        return self.health <= 0


class SoloDange:
    def __init__(self, dange_id, player_id):
        self.full_log = []
        self.turn_counter = 0
        self.full_log.append(('c', "Прохождение данжа началось! Удачи, боец!", self.turn_counter))
        self.dange_id = dange_id
        self.player_id = player_id
        dange_info = db.get_dange_main_info(self.dange_id)
        self.dange_name = dange_info[0]
        self.dange_amount_of_fights = dange_info[1]
        self.dange_filename = dange_info[2]
        enemy_list_ids = db.get_all_mobs_ids_on_dange(self.dange_id)
        self.mobs_list = []  # Actual list of Mob objects (only alive ones)
        mobs_info_log_text = "Твои соперники (Здоровье, Броня): "
        for enemy_id in enemy_list_ids:
            self.mobs_list.append(Mob(enemy_id))
            mobs_info_log_text += str(self.mobs_list[-1].name)
            mobs_info_log_text += f" ({str(self.mobs_list[-1].health)}, {str(self.mobs_list[-1].armor_state)})"
            if len(self.mobs_list) != self.dange_amount_of_fights:
                mobs_info_log_text += ", "
        self.full_log.append(('c', mobs_info_log_text, self.turn_counter))
        self.turn = -1  # -1 is for player move, all the following numbers for mobs where self.turn is idx in mobs_list
        self.player_in_game = PlayerInGame(self.player_id, False, self.full_log, self.turn_counter)

    def process_player_turn(self, turn: Turn) -> None:
        self.full_log.append(('d', f"""
                                        Новый ход игрока.
                                    """, self.turn_counter))

        if turn.turn_type == TurnType.PHYSICAL_ATTACK:
            attack = Attack(self.player_in_game.weapon,
                            0,
                            turn.turn_type,
                            self.player_in_game.physical_dmg_incr,
                            self.player_in_game.stun_chance,
                            self.player_in_game.crit_chance,
                            self.player_in_game.bleeding_chance,
                            self.player_in_game.armor_ignore_chance,
                            self.player_in_game.vampirism_perc,
                            self.player_in_game.element_dmg_incr,
                            self.full_log,
                            self.turn_counter
                            )

            defender.apply_damage(defence.combined_damage)
            self.full_log.append(('c', f"""
                                            Игрок {defender.user_nick} получает {defence.combined_damage} урона! 
                                            Здоровье: {defender.health}. 
                                            Броня: {defender.armor_state}.
                                        """, self.turn_counter))

            defender.apply_bleeding_damage(self.full_log, self.turn_counter)

            attacker.health = min(attacker.health + defence.vampirism_cashback, 100)
            self.full_log.append(('c', f"""
                                            Игрок {attacker.user_nick} получает {defence.vampirism_cashback} здоровья 
                                            от нанесенного урона за счёт своих способностей!
                                            Здоровье: {attacker.health}. 
                                            Броня: {attacker.armor_state}.
                                        """, self.turn_counter))

            attacker.apply_damage(defence.mirror_dmg)
            self.full_log.append(('c', f"""
                                            Игрок {attacker.user_nick} получает {defence.mirror_dmg} обратного урона 
                                            за счёт способностей оппонента!
                                            Здоровье: {attacker.health}. 
                                            Броня: {attacker.armor_state}.
                                        """, self.turn_counter))

        elif turn.turn_type == TurnType.MAGIC_ATTACK:
            ability_attack = AbilityAttack(attacker.weapon.strength, turn.ability_obj, self.full_log, self.turn)
            self.full_log.append(('c', f"""
                                            Игрок {attacker.user_nick} применяет способность 
                                            {ability_attack.ability_used_name}!
                                        """, self.turn_counter))

            if int(ability_attack.target) == int(attacker.user_id):
                attacker.health = min(100, attacker.health + (attacker.health * ability_attack.heal_perc / 100))
                self.full_log.append(('c', f"""
                                                Игрок {attacker.user_nick} увеличивает свое здоровье на {ability_attack.heal_perc}%!
                                                Новый показатель здоровья: {attacker.health}
                                            """, self.turn_counter))
            else:
                defender.apply_damage(ability_attack.total_damage)
                self.full_log.append(('c', f"""
                                                Игрок {defender.user_nick} получает {ability_attack.total_damage} урона! 
                                                Здоровье: {defender.health}. 
                                                Броня: {defender.armor_state}.
                                            """, self.turn_counter))

            if ability_attack.is_stun == 1:
                defender.is_stuned = True

            if self.turn == 1:  # Sender turn
                self.possible_abilities_sender.remove(int(ability_attack.ability_id))
            else:
                self.possible_abilities_receiver.remove(int(ability_attack.ability_id))

        elif turn.turn_type == TurnType.CONSUME:
            pass

    # Returns current status of the duel:
    # 0 - if duel is still going on
    # 1 - if player had won
    # -1 - if player had lost
    def status(self) -> int:
        if not self.mobs_list:
            return 1
        if self.player_in_game.is_dead():
            return -1
        return 0

    def get_visible_logs_as_str(self) -> str:
        ans_logs = ""
        for (log_type, log, log_turn) in self.full_log:
            if log_type == 'c':
                ans_logs += log
                ans_logs += "\n"
        return ans_logs

    def get_visible_logs_as_str_last_turn(self) -> str:
        ans_logs = ""
        for (log_type, log, log_turn) in self.full_log:
            if log_type == 'c' and log_turn == self.turn_counter - 1:
                ans_logs += log
                ans_logs += "\n"
        return ans_logs


# Global dictionary to hold all ongoing solo danges in memory
# Key: solo_dange_id -> int
# Value: solo_dange_object -> class SoloDange
solo_danges_ongoing_dict = {}


# Functions to operate with existing solo danges
def init_solo_dange(dange: SoloDange) -> None:
    solo_danges_ongoing_dict[dange.dange_id] = dange
    # db.start_duel(dange.dange_id)


def kill_solo_dange(dange_id: int) -> None:
    killed_dange = solo_danges_ongoing_dict.pop(dange_id)
    if killed_dange.status() == 0:
        logging.warning("kill_solo_dange() call on ongoing solo dange with SoloDange::status() == 0!")
    # db.finish_duel(duel_id, killed_duel.status())
