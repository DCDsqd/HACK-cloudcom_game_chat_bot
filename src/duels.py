from equipment import *

from enum import Enum
import random
import threading


class TurnType(Enum):
    PHYSICAL_ATTACK = 1
    MAGIC_ATTACK = 2
    CONSUME = 3


class MagicAction:
    def __init__(self,
                 target_nick,  # '1' for every teammate, '-1' for every enemy
                 armor_repair,
                 health_heal,
                 stun,
                 miss_chance,
                 no_damage):
        self.target_nick = target_nick
        self.armor_repair = armor_repair
        self.health_heal = health_heal
        self.stun = stun
        self.miss_chance = miss_chance
        self.no_damage = no_damage


def switch_magic_action_name_to_action_obj(magic_action_target: str, magic_action_name: str) -> MagicAction:
    if magic_action_name == 'Каменная броня':
        return MagicAction(magic_action_target, 40, 0, 0, 0, 0)
    elif magic_action_name == 'Первородная благодетель':
        return MagicAction(magic_action_target, 0, 60, 0, 0, 0)
    elif magic_action_name == 'Плотная кожа':
        return MagicAction(magic_action_target, 0, 35, 0, 0, 0)
    elif magic_action_name == 'Проводник':
        return MagicAction(magic_action_target, 0, 0, 1, 0, 0)
    elif magic_action_name == 'Проницатель':
        return MagicAction(magic_action_target, 0, 0, 0, 1, 0)
    elif magic_action_name == 'Мраморное касание':
        return MagicAction(magic_action_target, 0, 0, 1, 0, 1)
    else:
        logging.error("switch_magic_action_name_to_action_obj() function got unknown magic_action_name!")


class Attack:
    def __init__(self,
                 weapon,
                 magic_dmg,
                 turn_type: TurnType,
                 physical_dmg_incr,
                 stun_chance,
                 crit_chance,
                 bleeding_chance,
                 armor_ignore_chance,
                 vampirism_perc,
                 element_dmg_incr,
                 full_log: list,
                 cur_turn: int
                 ):
        self.physical_dmg = round(
            weapon.strength + weapon.strength * physical_dmg_incr / 100) if \
            turn_type == TurnType.PHYSICAL_ATTACK else 0
        full_log.append(('d',
                         f"Урон физической атаки = {self.physical_dmg} ({weapon.strength} + {physical_dmg_incr / 100}%", cur_turn))

        self.element_dmg = 0  # TODO: Figure out how to fill this field
        full_log.append(('d',
                         f"Дополнительный урон стихий = {self.element_dmg} ({weapon.element_strength} + {element_dmg_incr / 100}%", cur_turn))

        self.magic_dmg = magic_dmg if turn_type == TurnType.MAGIC_ATTACK else 0
        full_log.append(('d',
                         f"Магический урон = {self.magic_dmg}", cur_turn))

        self.is_stun = 0
        if random.randint(1, 100) <= stun_chance:
            full_log.append(('d',
                             f"Атака является станом! Шанс стана был = {stun_chance / 100}%", cur_turn))
            full_log.append(('c',
                             f"Атакующий игрок наносит стан сопернику!", cur_turn))
            self.is_stun = 1
        else:
            full_log.append(('d',
                             f"Атака не является станом. Шанс стана был = {stun_chance / 100}%", cur_turn))

        self.is_crit = 0
        if turn_type == TurnType.PHYSICAL_ATTACK and random.randint(1, 100) <= crit_chance:
            full_log.append(('d',
                             f"Атака является критом! Шанс крита был = {crit_chance / 100}%", cur_turn))
            full_log.append(('c',
                             f"Атакующий игрок наносит критическую атаку по сопернику!", cur_turn))
            self.is_crit = 1
        else:
            full_log.append(('d',
                             f"Атака не является критом. Шанс крита был = {crit_chance / 100}%", cur_turn))

        self.is_bleeding = 0
        if random.randint(1, 100) <= bleeding_chance:
            full_log.append(('d',
                             f"Атака вызвала кровотечение! Шанс кровотечения был = {bleeding_chance / 100}%", cur_turn))
            full_log.append(('c',
                             f"Атакующий игрок вызывает кровотечение у соперника!"))
            self.is_bleeding = 1
        else:
            full_log.append(('d',
                             f"Атака не вызвала кровотечения. Шанс кровотечения был = {bleeding_chance / 100}%", cur_turn))

        self.has_ignored_armor = 0
        if random.randint(1, 100) <= armor_ignore_chance:
            full_log.append(('d',
                             f"Атака игнорирует вражескую броню! Шанс игнора брони был = {armor_ignore_chance / 100}%", cur_turn))
            full_log.append(('c',
                             f"Атакующий игрок за счет своих способностей игнорирует вражескую броню!", cur_turn))
            self.has_ignored_armor = 1
        else:
            full_log.append(('d',
                             f"Атака не игнорирует вражескую броню. Шанс игнора брони был = {armor_ignore_chance / 100}%", cur_turn))

        self.vampirism_perc = vampirism_perc
        full_log.append(('d',
                         f"Процент вамперизма атаки = {vampirism_perc}", cur_turn))


class Defence:
    def __init__(self,
                 attack: Attack,
                 armor_state,
                 physical_damage_decr,
                 magic_damage_decr,
                 element_damage_decr,
                 no_damage_chance,
                 mirror_damage_perc,
                 full_log: list,
                 cur_turn: int
                 ):
        self.physical_dmg = attack.physical_dmg
        self.element_dmg = attack.element_dmg
        self.magic_dmg = attack.magic_dmg
        self.is_crit = attack.is_crit
        # Critical attack increases physical damage by 1.5 times
        physical_damage_crit_mult = 1.5
        if self.is_crit:
            self.physical_dmg = round(self.physical_dmg * physical_damage_crit_mult)
            full_log.append(('d',
                             f"""
                                Так как атака является критической, физический урон увеличен в {physical_damage_crit_mult} раз.
                                Новое значение физического урона = {self.physical_dmg}.
                             """, cur_turn))
        self.is_stun = attack.is_stun
        self.is_bleeding = attack.is_bleeding
        if armor_state > 0 and not self.is_stun and not attack.has_ignored_armor:
            if random.randint(1, 100) <= no_damage_chance:
                self.physical_dmg = 0
                self.element_dmg = 0
                self.magic_dmg = 0
                full_log.append(('c', f"""
                                      Защищающийся игрок полностью игнорирует входящий урон за счет своих способностей!
                                      """, cur_turn))
            else:
                self.physical_dmg -= round(attack.physical_dmg * physical_damage_decr / 100)
                full_log.append(('d',
                                 f"Урон физической атаки после защиты = {self.physical_dmg} ({attack.physical_dmg} - {physical_damage_decr / 100}%", cur_turn))

                self.element_dmg -= round(attack.element_dmg * element_damage_decr / 100)
                full_log.append(('d',
                                 f"Доп урон стихий после защиты = {self.element_dmg} ({attack.element_dmg} - {element_damage_decr / 100}%", cur_turn))

                self.magic_dmg -= round(attack.magic_dmg * magic_damage_decr / 100)
                full_log.append(('d',
                                 f"Урон магической атаки после защиты = {self.magic_dmg} ({attack.magic_dmg} - {magic_damage_decr / 100}%", cur_turn))

        weapon_damage = self.physical_dmg + self.element_dmg
        self.combined_damage = weapon_damage + self.magic_dmg
        self.vampirism_cashback = round(weapon_damage * attack.vampirism_perc / 100)
        self.mirror_dmg = round(self.combined_damage * mirror_damage_perc / 100)


class PlayerInGame:
    def __init__(self, user_id_, beer_buff: bool, full_log: list, cur_turn: int):
        self.user_id = user_id_
        self.user_nick = db.get_user_nick(self.user_id)
        self.health = 100
        if beer_buff:
            self.health += 10
            full_log.append(('c', f"Игрок {self.user_nick} получает бафф в 10 очков здоровья от выпитого пива перед боем!", cur_turn))
        self.is_bleeding = False
        self.is_stuned = False

        # Armor fields
        self.armor = Armor(db.get_user_active_armor_meta_id(self.user_id))
        self.armor_state = self.armor.strength
        self.mirror_dmg_perc = 0
        self.physical_damage_decr = 0
        self.magic_damage_decr = 0
        self.element_damage_decr = 0
        self.no_damage_chance = 0
        self.apply_armor_bonuses()
        full_log.append(('с', f"Игрок {self.user_nick} выбрал для защиты {self.armor.name}!", cur_turn))

        # Weapon fields
        self.weapon = Weapon(db.get_user_active_weapon_meta_id(self.user_id))
        self.physical_dmg_incr = 0
        self.stun_chance = 0
        self.crit_chance = 5
        self.bleeding_chance = 0
        self.armor_ignore_chance = 1
        self.vampirism_perc = 0
        self.element_dmg_incr = 0
        self.apply_weapon_bonuses()
        full_log.append(('c', f"Игрок {self.user_nick} будет атаковать с помощью {self.weapon.name}!", cur_turn))

    def is_dead(self) -> bool:
        return self.health <= 0

    def apply_armor_bonuses(self) -> None:
        for ench in self.armor.enchantments_list:
            self.armor_state += ench.health_buff
            self.mirror_dmg_perc += ench.mirror_dmg_perc
            self.physical_damage_decr += ench.physical_damage_decr
            self.magic_damage_decr += ench.magic_damage_decr
            self.element_damage_decr += ench.element_damage_decr
            self.no_damage_chance += ench.no_damage_chance

    def apply_weapon_bonuses(self) -> None:
        for ench in self.weapon.enchantments_list:
            self.physical_dmg_incr += ench.physical_dmg_incr
            self.stun_chance += ench.stun_chance
            self.crit_chance += ench.crit_chance
            self.bleeding_chance += ench.bleeding_chance
            self.armor_ignore_chance += ench.armor_ignore_chance
            self.vampirism_perc += ench.vampirism_perc
            self.element_dmg_incr += ench.element_dmg_incr

    def apply_damage(self, damage: int) -> None:
        self.armor_state -= damage
        print(f"in apply damage now armor state = {self.armor_state}, damage {damage}")
        print(f"in apply damage health had= {self.health}")
        if self.armor_state < 0:
            self.health -= abs(self.armor_state)
            self.armor_state = 0
        print(f"in apply damage now health = {self.health}")

    # Checks if Player has bleeding effect on him and applies damage if so
    # Returns True if damage was applied, False otherwise
    # NOTE: Bleeding effect always applies directly to health ignoring armor
    def apply_bleeding_damage(self, full_log: list, cur_turn: int) -> bool:
        if self.is_bleeding:
            self.health -= 5
            full_log.append(('c', f"Игрок {self.user_nick} получает урон от активного кровотечения! Здоровье: {self.health}", cur_turn))
            return True
        return False


class Turn:
    def __init__(self, turn_maker_, turn_type_: TurnType, target_, magic_action_name='', magic_action_target=''):
        if magic_action_target == '' and turn_type_ == TurnType.MAGIC_ATTACK:
            magic_action_target = db.get_user_nick(turn_maker_)

        self.turn_maker = turn_maker_
        self.turn_type = turn_type_
        self.target = target_

        # Magic attack field, None if turn_type != MAGIC_ATTACK
        self.magic_action = None
        if self.turn_type != TurnType.MAGIC_ATTACK:
            self.magic_action = switch_magic_action_name_to_action_obj(magic_action_target, magic_action_name)


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

        logging.info(f"Started duel between (from duel constructor) {self.sender_player.user_id} and {self.receiver_player.user_id}, duel id = {self.id}")

        self.full_log.append(('c', "Дуэль началась!", self.turn_counter))
        self.full_log.append(('d', f"""
                                        Конструктор дуэли завершил работу. 
                                        Sender_id = {self.sender_player.user_id},
                                        Receiver_id = {self.receiver_player.user_id},
                                        Duel_id = {self.id}
                                    """, self.turn_counter))

    def process_turn(self, turn: Turn) -> None:

        attacker = self.sender_player if turn.target == self.receiver_player.user_id else self.receiver_player
        defender = self.sender_player if turn.turn_maker == self.receiver_player.user_id else self.receiver_player

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

        if turn.turn_type == TurnType.PHYSICAL_ATTACK or turn.turn_type == TurnType.MAGIC_ATTACK:
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

        elif turn.turn_type == TurnType.CONSUME:
            pass
        else:
            logging.warning("turn.turn_type which is of TurnType(Enum) type is not equal to any member of enum")

        self.turn_counter += 1
        if not defender.is_stuned:
            self.turn = 3 - self.turn  # Turn switch
        else:
            self.full_log.append(('c', f"""
                                            Игрок {defender.user_nick} пропускает свой ход, из-за того, 
                                            что находится в стане!
                                        """, self.turn_counter))
        self.full_log.append(('d', f"""
                                        Смена хода. self.turn = {self.turn}
                                    """, self.turn_counter))

    # Returns current status of the duel:
    # 0 - if duel is still going on
    # 1 - if player 1 has won
    # 2 - if player 2 has won
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

    def get_player_in_game(self, player_id):
        if int(self.sender_player.user_id) == int(player_id):
            return self.sender_player
        return self.receiver_player


# Global dictionary to hold all ongoing duels in memory
# Key: duel_id -> int
# Value: duel_object -> class Duel
duels_ongoing_dict = {}


# Functions to operate with existing duels
def init_duel(duel: Duel) -> None:
    duels_ongoing_dict[duel.id] = duel
    db.start_duel(duel.id)


def kill_duel(duel_id: int) -> None:
    killed_duel = duels_ongoing_dict.pop(duel_id)
    if killed_duel.status() == 0:
        logging.warning("kill_duel() call on ongoing duel with Duel::status() == 0!")
    db.finish_duel(duel_id, killed_duel.status())


# Returns list of Duel objects in which time to make current turn was in fact exceeded
# To every other element in array applies time decrement
def decrease_time_to_all_duels() -> list[Duel]:
    expired_duels = []
    for duel_id, duel_obj in duels_ongoing_dict.items():
        duel_obj.time_left_to_make_turn -= 1
        if duel_obj.time_left_to_make_turn < 1:
            expired_duels.append(duel_obj)
    return expired_duels
