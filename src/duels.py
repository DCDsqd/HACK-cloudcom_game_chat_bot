from common_battle import *


# This is a class that holds all the needed information about ongoing duel
# in memory in order for it to be more easily accessible.
# As soon as the duel ends the object should be destroyed.
class Duel:
    def __init__(self, duel_id_, sender_id_, receiver_id_):
        self.turn = 1  # 1 for sender turn, 2 for receiver turn
        self.turn_counter = 0

        # This is a list that hold all messages that were generated through-out the duel
        # First argument is responsible for type of the message
        # It could be:
        # - 'c' = critical message, that'll be displayed to the user
        # - 'd' = debug message, that won't be visible to user, but could be used to fully understand what's going on
        # Second argument is the actual message
        # This list is being passed through lots of functions to insert messages
        self.full_log = []

        self.full_log.append(('d', f"""
                                        Конструктор дуэли начал работу. 
                                        Sender_id = {sender_id_},
                                        Receiver_id = {receiver_id_},
                                        Duel_id = {duel_id_}
                                    """, self.turn))

        self.id = duel_id_
        self.time_left_to_make_turn = 30  # in seconds

        self.sender_player = PlayerInGame(sender_id_, False, self.full_log, self.turn_counter)
        self.receiver_player = PlayerInGame(receiver_id_, False, self.full_log, self.turn_counter)

        self.possible_abilities_sender = db.get_all_abilities_ids_for_class(db.get_player_class_by_id(self.sender_player.user_id))
        self.possible_abilities_receiver = db.get_all_abilities_ids_for_class(db.get_player_class_by_id(self.receiver_player.user_id))

        self.possible_consumales_sender = db.get_list_of_owned_consumables(self.sender_player.user_id)
        self.used_consumales_sender = []
        self.possible_consumales_receiver = db.get_list_of_owned_consumables(self.receiver_player.user_id)
        self.used_consumales_receiver = []

        logging.info(f"Started duel between (from duel constructor) {self.sender_player.user_id} and {self.receiver_player.user_id}, duel id = {self.id}")

        self.full_log.append(('c', "Дуэль началась!", self.turn_counter))
        self.full_log.append(('d', f"""
                                        Конструктор дуэли завершил работу. 
                                        Sender_id = {self.sender_player.user_id},
                                        Receiver_id = {self.receiver_player.user_id},
                                        Duel_id = {self.id}
                                    """, self.turn_counter))

    def process_turn(self, turn: Turn) -> None:

        attacker: PlayerInGame = self.sender_player if turn.target == self.receiver_player.user_id else self.receiver_player
        defender: PlayerInGame = self.sender_player if turn.turn_maker == self.receiver_player.user_id else self.receiver_player

        self.full_log.append(('d', f"""
                                    Новый ход. Нападает - {attacker.user_nick}, защищается - {defender.user_nick}. 
                                    Turn type = {turn.turn_type.name}.
                            """, self.turn_counter))

        if int(turn.target) != int(defender.user_id):
            logging.warning(f"""turn.target != defender.user_id in duel during process_turn() call, 
                                turn.turn_maker = {turn.turn_maker} (attacker={attacker.user_id}), 
                                turn.target = {turn.target} (defender={defender.user_id})""")
            pass
        if int(turn.turn_maker) != int(attacker.user_id):
            logging.warning(f"""turn.turn_maker != attacker.user_id in duel during process_turn() call, 
                                turn.turn_maker = {turn.turn_maker}, (attacker={attacker.user_id}), 
                                turn.target = {turn.target} (defender={defender.user_id})""")
            pass

        if turn.turn_type == TurnType.PHYSICAL_ATTACK:
            attack = Attack(attacker.weapon,
                            0,
                            turn.turn_type,
                            attacker.physical_dmg_incr,
                            attacker.stun_chance,
                            attacker.crit_chance,
                            attacker.bleeding_chance,
                            attacker.armor_ignore_chance,
                            attacker.vampirism_perc,
                            attacker.element_dmg_incr,
                            self.full_log,
                            self.turn_counter
                            )

            defence = Defence(attack,
                              defender.armor_state,
                              defender.physical_damage_decr,
                              defender.magic_damage_decr,
                              defender.element_damage_decr,
                              defender.no_damage_chance,
                              defender.mirror_dmg_perc,
                              self.full_log,
                              self.turn_counter
                              )

            defender.apply_damage(defence.combined_damage)
            self.full_log.append(('c', f"""
                                            ⚔️ Игрок {defender.user_nick} получает {defence.combined_damage} урона! 
                                            ❤️ Здоровье: {defender.health}. 
                                            🛡️ Броня: {defender.armor_state}.
                                        """, self.turn_counter))

            defender.apply_bleeding_damage(self.full_log, self.turn_counter)

            attacker.health = min(attacker.health + defence.vampirism_cashback, 100)
            self.full_log.append(('c', f"""
                                            💖 Игрок {attacker.user_nick} получает {defence.vampirism_cashback} здоровья 
                                            от нанесенного урона за счёт своих способностей!
                                            ❤️ Здоровье: {attacker.health}. 
                                            🛡️ Броня: {attacker.armor_state}.
                                        """, self.turn_counter))

            if defence.vampirism_cashback == 0:
                tmp_list = list(self.full_log[-1])
                tmp_list[0] = 'd'
                self.full_log[-1] = tuple(tmp_list)

            attacker.apply_damage(defence.mirror_dmg)
            self.full_log.append(('c', f"""
                                            ⚔️ Игрок {attacker.user_nick} получает {defence.mirror_dmg} обратного урона 
                                            за счёт способностей оппонента!
                                            ❤️ Здоровье: {attacker.health}. 
                                            🛡️ Броня: {attacker.armor_state}.
                                        """, self.turn_counter))
            if defence.mirror_dmg == 0:
                tmp_list = list(self.full_log[-1])
                tmp_list[0] = 'd'
                self.full_log[-1] = tuple(tmp_list)

            defender.is_stuned = bool(defence.is_stun)

        elif turn.turn_type == TurnType.MAGIC_ATTACK:
            ability_attack = AbilityAttack(attacker.weapon.strength, turn.ability_obj, self.full_log, self.turn)
            self.full_log.append(('c', f"""
                                            🔮 Игрок {attacker.user_nick} применяет способность 
                                            {ability_attack.ability_used_name}!
                                        """, self.turn_counter))
            
            if int(ability_attack.target) == int(attacker.user_id):
                attacker.health = min(100, attacker.health + (attacker.health * ability_attack.heal_perc / 100))
                self.full_log.append(('c', f"""
                                                💖 Игрок {attacker.user_nick} увеличивает свое здоровье на {ability_attack.heal_perc}%!
                                                ❤️ Новый показатель здоровья: {attacker.health}
                                            """, self.turn_counter))
            else:
                defender.apply_damage(ability_attack.total_damage)
                self.full_log.append(('c', f"""
                                                ⚔️ Игрок {defender.user_nick} получает {ability_attack.total_damage} урона! 
                                                ❤️ Здоровье: {defender.health}. 
                                                🛡️ Броня: {defender.armor_state}.
                                            """, self.turn_counter))

            if ability_attack.is_stun == 1:
                defender.is_stuned = True

            if self.turn == 1:  # Sender turn
                self.possible_abilities_sender.remove(int(ability_attack.ability_id))
            else:
                self.possible_abilities_receiver.remove(int(ability_attack.ability_id))

        elif turn.turn_type == TurnType.CONSUME:
            attacker.apply_consumable_as_to_self(turn.consumable_obj, self.full_log, self.turn_counter)
            defender.apply_consumable_as_to_enemy(turn.consumable_obj, self.full_log, self.turn_counter)
            self.get_possible_consumables(attacker.user_id).remove(turn.consumable_obj.id)
            self.get_used_consumables(attacker.user_id).append(turn.consumable_obj.id)

        else:
            logging.warning("turn.turn_type which is of TurnType(Enum) type is not equal to any member of enum")

        if not defender.is_stuned:
            # Turn switch
            self.force_switch_turn()
        else:
            self.full_log.append(('c', f"""
                                            Игрок {defender.user_nick} пропускает свой ход, из-за того, что находится в стане!
                                        """, self.turn_counter))
            # Turn switch (renew)
            self.force_renew_turn()

        self.full_log.append(('d', f"""
                                        Смена хода. self.turn = {self.turn}
                                    """, self.turn_counter))

        # print(self.full_log)

    # Returns current status of the duel:
    # 0 - if duel is still going on
    # 1 - if player 1 had won
    # 2 - if player 2 had won
    def status(self) -> int:
        if self.sender_player.is_dead():
            return 2
        elif self.receiver_player.is_dead():
            return 1
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

    def get_player_in_game(self, player_id):
        if int(self.sender_player.user_id) == int(player_id):
            return self.sender_player
        return self.receiver_player

    def get_possible_abilities(self, player_id):
        if int(player_id) == int(self.sender_player.user_id):
            return self.possible_abilities_sender
        return self.possible_abilities_receiver

    def get_possible_consumables(self, player_id):
        if int(player_id) == int(self.sender_player.user_id):
            return self.possible_consumales_sender
        return self.possible_consumales_receiver

    def get_used_consumables(self, player_id):
        if int(player_id) == int(self.sender_player.user_id):
            return self.used_consumales_sender
        return self.used_consumales_receiver

    def force_switch_turn(self):
        self.turn = 3 - self.turn
        self.turn_counter += 1
        self.time_left_to_make_turn = 30

    def force_renew_turn(self, add_to_turn_counter: bool = True):
        if add_to_turn_counter:
            self.turn_counter += 1
        self.time_left_to_make_turn = 30

    def get_attacker_player_in_game(self) -> PlayerInGame:
        return self.sender_player if self.turn == 1 else self.receiver_player

    def get_defender_player_in_game(self) -> PlayerInGame:
        return self.sender_player if self.turn == 2 else self.receiver_player


# Global dictionary to hold all ongoing duels in memory
# Key: duel_id -> int
# Value: duel_object -> class Duel
duels_ongoing_dict = {}


# Functions to operate with existing duels
def init_duel(duel: Duel) -> None:
    duels_ongoing_dict[duel.id] = duel
    db.start_duel(duel.id)


def kill_duel(duel_id: int) -> None:
    killed_duel: Duel = duels_ongoing_dict.pop(duel_id)
    if killed_duel.status() == 0:
        logging.warning("kill_duel() call on ongoing duel with Duel::status() == 0!")
    db.finish_duel(duel_id, killed_duel.status())
    for cons_id in killed_duel.used_consumales_sender:
        db.use_consumable_for_user(killed_duel.sender_player.user_id, cons_id)
    for cons_id in killed_duel.used_consumales_receiver:
        db.use_consumable_for_user(killed_duel.receiver_player.user_id, cons_id)


# Returns list of Duel objects in which time to make current turn was in fact exceeded
# To every other element in array applies time decrement
def decrease_time_to_all_duels() -> list[Duel]:
    expired_duels = []
    for duel_id, duel_obj in duels_ongoing_dict.items():
        duel_obj.time_left_to_make_turn -= 1
        if duel_obj.time_left_to_make_turn < 1:
            expired_duels.append(duel_obj)
    return expired_duels
