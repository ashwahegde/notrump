from flask_login import UserMixin

from utils.db import (insert_row, select_query, update_rows, complex_query,
    check_user, get_passwordHash, init_db, select_query_dict
)

class User(UserMixin):
    def __init__(self,id):
        self.id = id
        self.userId = id
        self.roomId = None
        self.roomCode = None
    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)
    def set_roomId(self,roomId):
        self.roomId = roomId

    def set_roomUserId(self,roomUserId):
        self.roomUserId = roomUserId

    def set_roomCode(self,roomCode):
        self.roomCode = roomCode

    def to_json(self):
        return self.__dict__

    def from_json(self,dicted_user):
        self.roomId = dicted_user.get("roomId")
        self.roomUserId = dicted_user.get("roomUserId")
    def get_roomId(self):
        """
        check db for roomId
        """
        room_info = select_query_dict(**{
            "columns": ["roomId"],
            "filters": {
                "userId": self.userId,
            },
            "table_name": "roomStatus",
        })
        self.roomId = room_info.get("roomId")
        return self.roomId

    def get_roomCode(self):
        """
        get room code using room ID
        """
        if self.roomId:
            room_info = select_query_dict(**{
                "columns": ["roomCode"],
                "filters": {
                    # "host": self.userId,
                    "roomId": self.roomId,
                },
                "table_name": "roomInfo",
                "userId": self.userId,
            })
            if room_info:
                self.roomCode = room_info.get("roomCode")

    def get_joinedRoomId(self):
        """
        check db for roomId
        """
        room_info = select_query_dict(**{
            "columns": ["roomId"],
            "filters": {
                "userId": self.userId,
            },
            "table_name": "roomStatus",
            "userId": self.userId,
        })
        self.roomId = room_info.get("roomId")
