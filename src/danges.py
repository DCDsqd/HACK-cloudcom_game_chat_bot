from duels import *


class Mob:
    def __init__(self, mob_id):
        self.id = mob_id
        mob_info_list = db.get_mob_main_info(mob_id)
        self.name = mob_info_list[0]
        self.health = mob_info_list[1]
        self.attack = mob_info_list[2]
        self.armor_state = mob_info_list[3]


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
        for enemy_id in enemy_list_ids:
            self.mobs_list.append(Mob(enemy_id))
        self.turn = -1  # -1 is for player move, all the following numbers for mobs where self.turn is idx in mobs_list
        self.player_in_game = PlayerInGame(self.player_id, False, self.full_log, self.turn_counter)

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
