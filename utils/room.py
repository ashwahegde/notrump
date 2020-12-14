from flask_login import UserMixin

from utils.db import (insert_row, select_query, update_rows, complex_query,
    check_user, get_passwordHash, init_db, select_query_dict
)

class Room():
    def __init__(self,user=None,roomId=None):
        if not user and not roomId:
            raise Exception("roomId not available")
        if user:
            self.roomId = user.roomId
            self.roomCode = user.roomCode
            self.players = [user.userId]
        else:
            self.roomId = roomId
    def set_roomId(self,roomId):
        self.roomId = roomId





    def set_roomCode(self,roomCode):
        self.roomCode = roomCode

    def to_json(self):
        return self.__dict__

    def from_json(self,dicted_user):
        self.roomId = dicted_user.get("roomId")
        self.roomUserId = dicted_user.get("roomUserId")

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
            print(room_info)
            if room_info:
                self.roomCode = room_info.get("roomCode")

    def add_host(self,userId):
        """
        add user to roomStatus as well
        """
        roomUserId = 0
        try:
            insert_row(**{
                "userId": userId,
                "columns": {
                    "roomId": self.roomId,
                    "roomUserId": roomUserId,
                    "userId": userId,
                    "roomState": "0",
                    "points": 0,
                    "lastWon": 0,
                },
                "table_name": "roomStatus"
            })
        except Exception as e:
            current_app.logger.error('failed to insert user to roomStatus')
            current_app.logger.error(f'e')

    def add_user(self,userId):
        """
        add user to roomStatus as well
        """
        self.players = self.read_players()
        assert len(self.players) < 4
        assert userId not in self.players
        self.players.append(userId)
        roomUserId = len(self.players)
        try:
            insert_row(**{
                "userId": userId,
                "columns": {
                    "roomId": self.roomId,
                    "roomUserId": roomUserId,
                    "userId": userId,
                    "roomState": "0",
                    "points": 0,
                    "lastWon": 0,
                },
                "table_name": "roomStatus"
            })
        except Exception as e:
            current_app.logger.error('failed to insert user to roomStatus')
            current_app.logger.error(f'e')

    def read_players(self):
        cursor = select_query(**{
            "columns": ["userId","roomUserId"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomStatus",
            "userId": self.roomId,
        })
        players = []
        manyRow = cursor.fetchmany(4)
        if not manyRow:
            return []
        for arow in manyRow:
            players.append(arow[0])
        print(players)
        return players
