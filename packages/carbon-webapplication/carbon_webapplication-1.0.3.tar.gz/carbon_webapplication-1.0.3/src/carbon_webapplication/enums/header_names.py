from enum import Enum

class HeaderNames(str, Enum):
    def __str__(self):
        return str(self.name)
    Authorization = "Authorization"
    Bearer = "Bearer"