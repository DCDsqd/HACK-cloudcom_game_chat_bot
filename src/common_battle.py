from equipment import *

from enum import Enum
import random


class TurnType(Enum):
    PHYSICAL_ATTACK = 1
    MAGIC_ATTACK = 2
    CONSUME = 3


class Consumable:
    def __init__(self, consumable_id: int, target: int):
        self.id = consumable_id
        self.target = target
        cons_info_list = db.get_consumable_main_info(consumable_id)
        self.name = cons_info_list[0]
        self.buff_id = cons_info_list[1]
        self.area = cons_info_list[2]
        self.target_type = cons_info_list[3]
        self.buff_name = 0
        self.is_stun = 0
        self.damage = 0
        self.armor_regen = 0
        if self.buff_id != 0:
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
        if consumable.target_type == "friend" or consumable.target_type == "all":
            self.apply_consumable_straight_forward(consumable)
            self.consumable_log_affect(consumable, full_log, cur_turn)

    def apply_consumable_as_to_teammate(self, consumable: Consumable, full_log: list, cur_turn: int) -> None:
        if (consumable.target_type == "friend" or consumable.target_type == "all") and int(consumable.area) == 1:
            self.apply_consumable_straight_forward(consumable)
            self.consumable_log_affect(consumable, full_log, cur_turn)

    # NOTE: This does not check 'area' field of consumable object!
    def apply_consumable_as_to_enemy(self, consumable: Consumable, full_log: list, cur_turn: int) -> None:
        if consumable.target_type == "enemy":
            self.apply_consumable_straight_forward(consumable)
            self.consumable_log_affect(consumable, full_log, cur_turn)


class Turn:
    def __init__(self, turn_maker_, turn_type_: TurnType, target_, ability_obj: Ability = None, consumable_obj: Consumable = None):
        self.turn_maker = turn_maker_
        self.turn_type = turn_type_
        self.target = target_
        self.ability_obj = ability_obj
        self.consumable_obj = consumable_obj
