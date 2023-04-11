from database import *


class Duel:
    def __init__(self, duel_id_, sender_id_, receiver_id_):
        self.id = duel_id_
        self.sender_id = sender_id_
        self.receiver_id = receiver_id_
        self.turn = 1
