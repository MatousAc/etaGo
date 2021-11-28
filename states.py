import enum
class state(int, enum.Enum):
    DISCONNECTED        : int = 0
    CONNECTED           : int = 1
    READY_TO_START_GAME : int = 2
    PLAYING_GAME        : int = 3
    WAITING_FOR_OTHERS  : int = 4
    PLAYING             : int = 5
    END_OF_GAME         : int = 6