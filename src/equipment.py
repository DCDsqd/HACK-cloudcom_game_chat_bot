from database import *


# List to keep all the enchantments in the memory while bot is up
# and do not bother actual database with small queries
# NOTE: This implementation leads to necessary restart if you've
# made some changes to enchantments in the database
armor_enchantments_dict = {}
weapon_enchantments_dict = {}


class ArmorEnchantment:
    def __init__(self, id_):
        self.id = id_
        info_list = db.load_armor_enchantments_perks(self.id)
        self.name = info_list[0]
        self.mirror_dmg_perc = info_list[1]
        self.physical_damage_decr = info_list[2]
        self.magic_damage_decr = info_list[3]
        self.element_damage_decr = info_list[4]
        self.no_damage_chance = info_list[5]
        self.health_buff = info_list[6]


class WeaponEnchantment:
    def __init__(self, id_):
        self.id = id_
        info_list = db.load_weapon_enchantments_perks(self.id)
        self.name = info_list[0]
        self.physical_dmg_incr = info_list[1]
        self.stun_chance = info_list[2]
        self.crit_chance = info_list[3]
        self.bleeding_chance = info_list[4]
        self.armor_ignore_chance = info_list[5]
        self.vampirism_perc = info_list[6]
        self.element_dmg_incr = info_list[7]


# Initializes all enchants dictionaries at the start of the program (called in main)
def init_all_enchantments() -> None:
    all_armor_enchantments_ids = db.get_all_armor_enchantments_ids()
    for cur_id in all_armor_enchantments_ids:
        armor_enchantments_dict[cur_id] = ArmorEnchantment(cur_id)
    all_weapon_enchantments_ids = db.get_all_weapon_enchantments_ids()
    for cur_id in all_weapon_enchantments_ids:
        weapon_enchantments_dict[cur_id] = WeaponEnchantment(cur_id)
    logging.info("Finished initializing global enchantment arrays")


# Returns list of ArmorEnchantment objects from given list of armor enchants ids
def armor_enchants_id_to_objects_list(enchants_ids: list) -> list:
    result_list = []
    for i in enchants_ids:
        result_list.append(armor_enchantments_dict[int(i)])
    return result_list


# Returns list of WeaponEnchantment objects from given list of weapon enchants ids
def weapon_enchants_id_to_objects_list(enchants_ids: list) -> list:
    result_list = []
    for i in enchants_ids:
        result_list.append(weapon_enchantments_dict[int(i)])
    return result_list


class Armor:
    def __init__(self, meta_id_):
        self.meta_id = meta_id_
        info_list = db.load_all_item_info_for_battle_from_meta(self.meta_id)
        self.base_id = info_list[0]
        self.enchantments_list = armor_enchants_id_to_objects_list(str(info_list[1]).split(','))
        self.name = info_list[2]
        self.strength = info_list[3]


class Weapon:
    def __init__(self, meta_id_):
        self.meta_id = meta_id_
        info_list = db.load_all_item_info_for_battle_from_meta(self.meta_id)
        self.base_id = info_list[0]
        self.enchantments_list = weapon_enchants_id_to_objects_list(str(info_list[1]).split(','))
        self.name = info_list[2]
        self.strength = info_list[3]

