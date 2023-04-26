from equipment import *

from enum import Enum
import random
import re


class TurnType(Enum):
    PHYSICAL_ATTACK = 1
    MAGIC_ATTACK = 2
    CONSUME = 3


class Consumable:
    def __init__(self, consumable_id: int):
        self.id = consumable_id
        cons_info_list = db.get_consumable_main_info(consumable_id)
        self.name = cons_info_list[0]
        self.buff_id = cons_info_list[1]
        self.area = cons_info_list[2]
        self.target = cons_info_list[3]
        buff_info = db.get_buff_info(self.buff_id)
        self.buff_name = buff_info[0]
        self.is_stun = buff_info[1]
        self.damage = buff_info[2]
        self.armor_regen = buff_info[4]


class Ability:
    def __init__(self, abil_id, target: int):
        self.id = abil_id
        self.target = target
        ability_info = db.get_ability_main_info(abil_id)
        self.name = ability_info[0]
        self.buff_id = ability_info[1]
        self.dmg_perc = ability_info[2]
        self.is_area = ability_info[3]
        self.target_type = ability_info[4]
        buff_info = db.get_buff_info(self.buff_id) if self.buff_id != 0 else [0, 0, 0, 0, 0]
        self.buff_name = buff_info[0]
        self.is_stun = buff_info[1]
        self.dmg = abs(buff_info[2])
        # self.defence_perc = buff_info[3]
        # self.miss_perc = buff_info[4]


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


class AbilityAttack:
    def __init__(self,
                 regular_weapon_dmg: int,
                 ability_obj: Ability,
                 full_log: list,
                 cur_turn: int
                 ):
        self.ability_used_name = ability_obj.name
        self.ability_id = db.get_ability_id_from_name(self.ability_used_name)
        self.buff_used_name = ability_obj.buff_name
        full_log.append(('d',
                         f"Используется способность = {self.ability_used_name}!",
                         cur_turn))
        full_log.append(('d',
                         f"Используется бафф = {self.buff_used_name}!",
                         cur_turn))

        self.dmg_perc = 0
        self.heal_perc = 0
        if ability_obj.dmg_perc >= 0:
            self.dmg_perc = ability_obj.dmg_perc
        else:
            self.heal_perc = abs(ability_obj.dmg_perc)

        self.total_damage = regular_weapon_dmg + (regular_weapon_dmg * self.dmg_perc/100) + ability_obj.dmg
        full_log.append(('d',
                         f"Полный урон от абилки = {self.total_damage} ((обычный урон от оружия [{regular_weapon_dmg}] + {self.dmg_perc}%) + дополнительный урон [{ability_obj.dmg}])",
                         cur_turn))

        self.is_area = ability_obj.is_area
        self.is_stun = ability_obj.is_stun
        self.target = ability_obj.target
        self.target_type = ability_obj.target_type


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
        # print(f"in apply damage now armor state = {self.armor_state}, damage {damage}")
        # print(f"in apply damage health had= {self.health}")
        if self.armor_state < 0:
            self.health -= abs(self.armor_state)
            self.armor_state = 0
        # print(f"in apply damage now health = {self.health}")

    # Checks if Player has bleeding effect on him and applies damage if so
    # Returns True if damage was applied, False otherwise
    # NOTE: Bleeding effect always applies directly to health ignoring armor
    def apply_bleeding_damage(self, full_log: list, cur_turn: int) -> bool:
        if self.is_bleeding:
            self.health -= 5
            full_log.append(('c', f"💔 Игрок {self.user_nick} получает урон от активного кровотечения! Здоровье: {self.health}", cur_turn))
            return True
        return False

    def apply_consumable_straight_forward(self, consumable: Consumable):
        self.armor_state += consumable.armor_regen
        if consumable.damage < 0:
            self.health += abs(consumable.damage)
        else:
            self.apply_damage(consumable.damage)
        self.is_stuned = consumable.is_stun

    def consumable_log_affect(self, consumable: Consumable, full_log: list, cur_turn: int):
        full_log.append(('c', f"⭐ Расходник {consumable.name} применен к {self.user_nick}!", cur_turn))
        if consumable.armor_regen != 0:
            full_log.append(('c',
                             f"🛡️ {self.user_nick} получает повышение брони на {consumable.armor_regen} единиц! Броня: {self.armor_state}",
                             cur_turn))
        if consumable.damage != 0:
            if consumable.damage < 0:
                full_log.append(('c',
                                 f"💖 {self.user_nick} получает восстановление здоровья на {abs(consumable.damage)} единиц! Здоровье: {self.health}",
                                 cur_turn))
            else:
                full_log.append(('c',
                                 f"💔 {self.user_nick} получает урон в {consumable.damage} единиц! Здоровье: {self.health}",
                                 cur_turn))
        if consumable.is_stun:
            full_log.append(('c',
                             f"Игрок {self.user_nick} попадает в стан!",
                             cur_turn))

    def apply_consumable_as_to_self(self, consumable: Consumable, full_log: list, cur_turn: int) -> None:
        if consumable.target == "friend" or consumable.target == "all":
            self.apply_consumable_straight_forward(consumable)
            self.consumable_log_affect(consumable, full_log, cur_turn)

    def apply_consumable_as_to_teammate(self, consumable: Consumable, full_log: list, cur_turn: int) -> None:
        if (consumable.target == "friend" or consumable.target == "all") and int(consumable.area) == 1:
            self.apply_consumable_straight_forward(consumable)
            self.consumable_log_affect(consumable, full_log, cur_turn)

    # NOTE: This does not check 'area' field of consumable object!
    def apply_consumable_as_to_enemy(self, consumable: Consumable, full_log: list, cur_turn: int) -> None:
        if consumable.target == "enemy":
            self.apply_consumable_straight_forward(consumable)
            self.consumable_log_affect(consumable, full_log, cur_turn)


class Turn:
    def __init__(self, turn_maker_, turn_type_: TurnType, target_, ability_obj: Ability = None, consumable_obj=None):
        self.turn_maker = turn_maker_
        self.turn_type = turn_type_
        self.target = target_
        self.ability_obj = ability_obj
        self.consumable_obj = consumable_obj


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

            defender.is_stuned = defence.is_stun

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
