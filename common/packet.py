from enum import Enum

class PacketType(Enum):
    CLIENT_JOIN = 0
    CLIENT_LEAVE = 1

    GAME_START = 2
    GAME_END = 3

    SET_WORD = 10
    SET_DRAWER = 11
    SET_LEFT_TIME = 12

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