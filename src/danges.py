from common_battle import *


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

    def apply_physical_attack(self, attack: Attack, full_damage: int, full_log: list, cur_turn: int) -> None:
        self.is_bleeding = attack.is_bleeding
        self.is_stunned = attack.is_stun
        self.apply_raw_damage(full_damage, attack.has_ignored_armor)

    def apply_magic_attack(self, ability_attack: AbilityAttack):
        self.is_stunned = ability_attack.is_stun
        self.apply_raw_damage(ability_attack.total_damage, False)

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
        self.possible_abilities_player = db.get_all_abilities_ids_for_class(db.get_player_class_by_id(self.player_in_game.user_id))

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

            full_damage = attack.physical_dmg
            if attack.is_crit:
                full_damage *= 1.5
            self.mobs_list[turn.target].apply_physical_attack(attack, full_damage, self.full_log, self.turn_counter)
            self.full_log.append(('c', f"""
                                            Моб {self.mobs_list[turn.target].name} получает {full_damage} урона! 
                                            Здоровье: {self.mobs_list[turn.target].health}. 
                                            Броня: {self.mobs_list[turn.target].armor_state}.
                                        """, self.turn_counter))
            final_vampirism_cashback = 0
            if attack.vampirism_perc != 0:
                final_vampirism_cashback = round(full_damage / 100 * attack.vampirism_perc)

            self.player_in_game.health = min(self.player_in_game.health + final_vampirism_cashback, 100)

        elif turn.turn_type == TurnType.MAGIC_ATTACK:
            ability_attack = AbilityAttack(self.player_in_game.weapon.strength, turn.ability_obj, self.full_log, self.turn)
            self.full_log.append(('c', f"""
                                            Игрок {self.player_in_game.user_nick} применяет способность 
                                            {ability_attack.ability_used_name}!
                                        """, self.turn_counter))

            if int(ability_attack.target) == int(self.player_in_game.user_id):
                self.player_in_game.health = min(100, self.player_in_game.health + (self.player_in_game.health * ability_attack.heal_perc / 100))
                self.full_log.append(('c', f"""
                                                Игрок {self.player_in_game.user_nick} увеличивает свое здоровье на {ability_attack.heal_perc}%!
                                                Новый показатель здоровья: {self.player_in_game.health}
                                            """, self.turn_counter))
            else:
                if ability_attack.is_area:
                    for mob in self.mobs_list:
                        mob.apply_magic_attack(
                            AbilityAttack(self.player_in_game.weapon.strength, turn.ability_obj, self.full_log, self.turn))
                        self.full_log.append(('c', f"""
                                                    Моб {mob.name} получает {ability_attack.total_damage} урона! 
                                                    Здоровье: {mob.health}. 
                                                    Броня: {mob.armor_state}.
                                                """, self.turn_counter))
                else:
                    self.mobs_list[turn.target].apply_magic_attack(AbilityAttack(self.player_in_game.weapon.strength, turn.ability_obj, self.full_log, self.turn))
                    self.full_log.append(('c', f"""
                                                    Моб {self.mobs_list[turn.target].name} получает {ability_attack.total_damage} урона! 
                                                    Здоровье: {self.mobs_list[turn.target].health}. 
                                                    Броня: {self.mobs_list[turn.target].armor_state}.
                                                """, self.turn_counter))

            self.possible_abilities_player.remove(int(ability_attack.ability_id))

        elif turn.turn_type == TurnType.CONSUME:
            pass

        for i in range(len(self.mobs_list)):
            if self.mobs_list[i].is_dead():
                self.mobs_list.remove(self.mobs_list[i])
                i -= 1

        self.turn_counter += 1
        self.turn += 1
        if self.turn >= len(self.mobs_list):
            self.turn = -1

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
                ans_logs += log.strip()
                ans_logs += "\n"
        ans_logs = re.sub(' {2,}', ' ', ans_logs)
        ans_logs = re.sub('\t ', '\n\n', ans_logs)
        ans_logs = re.sub('\t', '\n\n', ans_logs)
        ans_logs = re.sub('\n\n', '\n', ans_logs)
        return ans_logs

    def get_visible_logs_as_str_last_turn(self) -> str:
        ans_logs = ""
        for (log_type, log, log_turn) in self.full_log:
            if log_type == 'c' and log_turn == self.turn_counter - 1:
                ans_logs += log.strip()
                ans_logs += "\n"
        ans_logs = re.sub(' {2,}', ' ', ans_logs)
        ans_logs = re.sub('\t ', '\n\n', ans_logs)
        ans_logs = re.sub('\t', '\n\n', ans_logs)
        ans_logs = re.sub('\n\n', '\n', ans_logs)
        return ans_logs


# Global dictionary to hold all ongoing solo danges in memory
# Key: solo_dange_id -> int
# Value: solo_dange_object -> class SoloDange
solo_danges_ongoing_dict = {}


# Functions to operate with existing solo danges
def init_solo_dange(dange: SoloDange) -> None:
    solo_danges_ongoing_dict[dange.dange_id] = dange


def kill_solo_dange(dange_id: int) -> None:
    killed_dange = solo_danges_ongoing_dict.pop(dange_id)
    if killed_dange.status() == 0:
        logging.warning("kill_solo_dange() call on ongoing solo dange with SoloDange::status() == 0!")
    # db.finish_duel(duel_id, killed_duel.status())  # TODO: Make similar method here!!
