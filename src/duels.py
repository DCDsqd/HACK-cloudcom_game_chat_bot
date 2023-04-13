from database import *
from equipment import *
from enum import Enum


class PlayerInGame:
    def __init__(self, user_id_):
        self.user_id = user_id_
        self.health = 100

        # Armor fields
        self.armor = Armor(db.get_user_active_armor_meta_id(self.user_id))
        self.armor_state = self.armor.strength
        self.apply_armor_bonuses()
        self.mirror_dmg = 0
        self.physical_damage_decr = 0
        self.magic_damage_decr = 0
        self.element_damage_decr = 0
        self.no_damage_chance = 0

        # Weapon fields
        self.weapon = Weapon(db.get_user_active_weapon_meta_id(self.user_id))
        self.physical_dmg_incr = 0
        self.stun_chance = 0
        self.crit_chance = 5
        self.bleeding_chance = 0
        self.armor_ignore_chance = 1
        self.vampirism = 0
        self.element_dmg_incr = 0

    def is_dead(self) -> bool:
        return self.health <= 0

    def apply_armor_bonuses(self):
        for ench in self.armor.enchantments_list:
            self.armor_state += ench.health_buff
            self.mirror_dmg += ench.mirror_dmg
            self.physical_damage_decr += ench.physical_damage_decr
            self.magic_damage_decr += ench.magic_damage_decr
            self.element_damage_decr += ench.element_damage_decr
            self.no_damage_chance += ench.no_damage_chance

    def apply_weapon_bonuses(self):
        for ench in self.weapon.enchantments_list:
            self.physical_dmg_incr += ench.physical_damage_incr
            self.stun_chance += ench.stun_chance
            self.crit_chance += ench.crit_chance
            self.bleeding_chance += ench.bleeding_chance
            self.armor_ignore_chance += ench.armor_ignore_chance
            self.vampirism += ench.vampirism
            self.element_dmg_incr += ench.element_dmg_incr


class TurnType(Enum):
    PHYSICAL_ATTACK = 1
    MAGIC_ATTACK = 2
    CONSUME = 3


class Turn:
    def __init__(self, turn_maker_, turn_type_: TurnType, target_):
        self.turn_maker = turn_maker_
        self.turn_type = turn_type_
        self.target = target_


class Duel:
    def __init__(self, duel_id_, sender_id_, receiver_id_):
        self.id = duel_id_
        self.turn = 1

        self.sender_player = PlayerInGame(sender_id_)
        self.receiver_player = PlayerInGame(receiver_id_)

        self.log = "Дуэль началась!"

    def process_turn(self, turn: Turn):
        pass # Process turn here

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

