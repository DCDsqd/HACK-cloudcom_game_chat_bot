from database import *
from equipment import *
from enum import Enum
import random


class TurnType(Enum):
    PHYSICAL_ATTACK = 1
    MAGIC_ATTACK = 2
    CONSUME = 3


class Attack:
    def __init__(self,
                 base_attack_strength,
                 turn_type: TurnType,
                 physical_dmg_incr,
                 stun_chance,
                 crit_chance,
                 bleeding_chance,
                 armor_ignore_chance,
                 vampirism_perc,
                 element_dmg_incr
                 ):
        self.physical_dmg = round(
            base_attack_strength.strength + base_attack_strength.strength * physical_dmg_incr / 100) if \
            turn_type == TurnType.PHYSICAL_ATTACK else 0
        self.element_dmg = 0  # TODO: Figure out how to fill this field
        self.magic_dmg = base_attack_strength.strength if turn_type == TurnType.MAGIC_ATTACK else 0
        self.is_stun = 1 if random.randint(1, 100) <= stun_chance else 0
        self.is_crit = 1 if random.randint(1, 100) <= crit_chance else 0
        self.is_bleeding = 1 if random.randint(1, 100) <= bleeding_chance else 0
        self.has_ignored_armor = 1 if random.randint(1, 100) <= armor_ignore_chance else 0
        self.vampirism_perc = vampirism_perc


class Defence:
    def __init__(self,
                 attack: Attack,
                 armor_state,
                 physical_damage_decr,
                 magic_damage_decr,
                 element_damage_decr,
                 no_damage_chance,
                 mirror_damage_perc
                 ):
        self.physical_dmg = attack.physical_dmg
        self.element_dmg = attack.element_dmg
        self.magic_dmg = attack.magic_dmg
        self.is_crit = attack.is_crit
        # Critical attack increases physical damage by 1.5 times
        if self.is_crit:
            self.physical_dmg = round(self.physical_dmg * 1.5)
        self.is_stun = attack.is_stun
        self.is_bleeding = attack.is_bleeding
        if armor_state > 0 and not self.is_stun and not attack.has_ignored_armor:
            if random.randint(1, 100) <= no_damage_chance:
                self.physical_dmg = 0
                self.element_dmg = 0
                self.magic_dmg = 0
            else:
                self.physical_dmg -= round(attack.physical_dmg * physical_damage_decr / 100)
                self.element_dmg -= round(attack.element_dmg * element_damage_decr / 100)
                self.magic_dmg -= round(attack.magic_dmg * magic_damage_decr / 100)
        weapon_damage = self.physical_dmg + self.element_dmg
        self.combined_damage = weapon_damage + self.magic_dmg
        self.vampirism_cashback = round(weapon_damage * attack.vampirism_perc / 100)
        self.mirror_dmg = round(self.combined_damage * mirror_damage_perc / 100)


class PlayerInGame:
    def __init__(self, user_id_):
        self.user_id = user_id_
        self.health = 100

        # Armor fields
        self.armor = Armor(db.get_user_active_armor_meta_id(self.user_id))
        self.armor_state = self.armor.strength
        self.apply_armor_bonuses()
        self.mirror_dmg_perc = 0
        self.physical_damage_decr = 0
        self.magic_damage_decr = 0
        self.element_damage_decr = 0
        self.no_damage_chance = 0
        self.apply_armor_bonuses()

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
            self.physical_dmg_incr += ench.physical_damage_incr
            self.stun_chance += ench.stun_chance
            self.crit_chance += ench.crit_chance
            self.bleeding_chance += ench.bleeding_chance
            self.armor_ignore_chance += ench.armor_ignore_chance
            self.vampirism_perc += ench.vampirism_perc
            self.element_dmg_incr += ench.element_dmg_incr

    def apply_damage(self, damage: int) -> None:
        self.armor_state -= damage
        if self.armor_state < 0:
            self.health -= abs(self.armor_state)
            self.armor_state = 0


class Turn:
    def __init__(self, turn_maker_, turn_type_: TurnType, target_):
        self.turn_maker = turn_maker_
        self.turn_type = turn_type_
        self.target = target_


class Duel:
    def __init__(self, duel_id_, sender_id_, receiver_id_):
        self.id = duel_id_
        self.turn = 1  # 1 for sender turn, 2 for receiver turn
        self.turn_counter = 0

        self.sender_player = PlayerInGame(sender_id_)
        self.receiver_player = PlayerInGame(receiver_id_)

        self.full_log = "Дуэль началась!"

    def process_turn(self, turn: Turn) -> None:

        attacker = self.sender_player if turn.target == self.receiver_player.user_id else self.receiver_player
        defender = self.sender_player if turn.turn_maker == self.receiver_player.user_id else self.receiver_player

        if turn.target != defender.user_id:
            logging.warning(f"""turn.target != defender.user_id in duel during process_turn() call, 
                                turn.turn_maker = {turn.turn_maker}, turn.target = {turn.target}""")
            pass
        if turn.turn_maker != attacker.user_id:
            logging.warning(f"""turn.turn_maker != attacker.user_id in duel during process_turn() call, 
                                turn.turn_maker = {turn.turn_maker}, turn.target = {turn.target}""")
            pass

        if turn.turn_type == TurnType.PHYSICAL_ATTACK:
            attack = Attack(attacker.weapon.strength,
                            turn.turn_type,
                            attacker.physical_dmg_incr,
                            attacker.stun_chance,
                            attacker.crit_chance,
                            attacker.bleeding_chance,
                            attacker.armor_ignore_chance,
                            attacker.vampirism_perc,
                            attacker.element_dmg_incr
                            )

            defence = Defence(attack,
                              defender.armor_state,
                              defender.physical_damage_decr,
                              defender.magic_damage_decr,
                              defender.element_damage_decr,
                              defender.no_damage_chance,
                              defender.mirror_dmg_perc
                              )

            defender.apply_damage(defence.combined_damage)
            attacker.health = max(attacker.health + defence.vampirism_cashback, 100)
            attacker.apply_damage(defence.mirror_dmg)

            # TODO: Apply bleeding effect here smh

        elif turn.turn_type == TurnType.MAGIC_ATTACK:
            pass  #
        elif turn.turn_type == TurnType.CONSUME:
            pass
        else:
            logging.warning("turn.turn_type which is of TurnType(Enum) type is not equal to any member of enum")

        self.turn_counter += 1
        self.turn = 3 - self.turn

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
