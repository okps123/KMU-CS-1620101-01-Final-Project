from enum import Enum

class PacketType(Enum):
    CLIENT_JOIN = 0
    CLIENT_JOIN_CONFIRM = 1

    CLIENT_LEAVE = 2

    GAME_START = 3
    GAME_END = 4

    ROUND_START = 5
    ROUND_END = 6
    
    GUESS_CORRECT = 10
    
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