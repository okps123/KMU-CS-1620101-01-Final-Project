from enum import Enum

class PacketType(Enum):
    GAME_START = 0
    GAME_END = 1

    SET_WORD = 2
    SET_DRAWER = 3
    SET_LEFT_TIME = 4

    DRAW = 20
    ERASE = 21
    CLEAR = 22

    CHAT = 30

class Packet:
    def __init__(self, type: PacketType, data: any):
        self.type = type
        self.data = data

    def __str__(self):
        return f'Packet(type={self.type}, data={self.data})'