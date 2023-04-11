from database import *


# List to keep all the enchantments in the memory while bot is up
# and do not bother actual database with small queries
# NOTE: This implementation leads to necessary restart if you've
# made some changes to enchantments in the database
armor_enchantments_list = []
weapon_enchantments_list = []


class ArmorEnchantment:
    def __init__(self, id_):
        self.id = id_
        info_list = db.load_armor_enchantments_perks(self.id)
        self.name = info_list[0]
        self.mirror_dmg = info_list[1]
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
        self.vampirism = info_list[6]
        self.element_dmg_incr = info_list[7]


def init_all_enchantments():
    all_armor_enchantments_ids = db.get_all_armor_enchantments_ids()
    for cur_id in all_armor_enchantments_ids:
        armor_enchantments_list.append(ArmorEnchantment(cur_id))
    all_weapon_enchantments_ids = db.get_all_weapon_enchantments_ids()
    for cur_id in all_weapon_enchantments_ids:
        weapon_enchantments_list.append(WeaponEnchantment(cur_id))
    logging.info("Finished initializing global enchantment arrays")


class Armor:
    def __init__(self, id_):
        self.id = id_
        self.enchantments_list = []
