from flask_login import UserMixin
from flask import current_app
from utils.db import (insert_row, select_query, update_rows, complex_query,
    check_user, get_passwordHash, get_roomCode, init_db, select_query_dict
)

from utils.cards import Card
class Room():
    def __init__(self,roomId,gameStarted=False):
        if not roomId:
            raise Exception("roomId not available")
        self.roomId = roomId
        self.players = self.read_players()
        self.host = self.get_hostUserId()
        if gameStarted:
            self.cards = {}
            self.get_cardsOfAllUsers()


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
                    "roomId": self.roomId,
                },
                "table_name": "roomInfo",
            })
            if room_info:
                self.roomCode = room_info.get("roomCode")
                return self.roomCode
        return None

    def validate_room(self):
        roomCode = self.get_roomCode()
        if not roomCode:
            return False
        if not roomCode == self.roomCode:
            return False
        return True

    def add_host(self,userId):
        """
        add user to roomStatus as well
        """
        roomUserId = 1
        try:
            insert_row(**{
                "userId": userId,
                "columns": {
                    "roomId": self.roomId,
                    "roomUserId": roomUserId,
                    "userId": userId,
                    "cards": "",
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
        assert len(self.players) < 4
        assert userId not in self.players
        self.players.append(userId)
        try:
            insert_row(**{
                "userId": userId,
                "columns": {
                    "roomId": self.roomId,
                    "userId": userId,
                    "cards": "",
                    "points": 0,
                    "lastWon": 0,
                },
                "table_name": "roomStatus"
            })
        except Exception as e:
            current_app.logger.error('failed to insert user to roomStatus')
            current_app.logger.error(f'{e}')

    def read_players(self):
        cursor = select_query(**{
            "columns": ["userId"],
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
        return players

    def get_hostUserId(self):
        cursor = select_query(**{
            "columns": ["host"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomInfo",
        })
        host = cursor.fetchone()
        if not host:
            return False
        else:
            return host[0]

    def is_userHost(self,userId):
        if userId == self.host:
            return True
        else:
            return False

    def add_playersToGame(self,playerChosen):
        #team-mate as 3
        update_rows(**{
            "table_name": "roomStatus",
            "columns": {
                "roomUserId": 3,
            },
            "filters": {
                "userId": playerChosen,
                "roomId": self.roomId,
            }
        })
        players = self.players
        players.remove(playerChosen)
        players.remove(self.host)
        for i,userId in enumerate(players):
            update_rows(**{
                "table_name": "roomStatus",
                "columns": {
                    "roomUserId": 2*i+2,
                },
                "filters": {
                    "userId": userId,
                    "roomId": self.roomId,
                }
            })

    def cancel_room(self):
        """remove all rows from roomStatus and roomInfo"""
        pass

    def is_gameStarted(self):
        room_info = select_query_dict(**{
            "columns": ["roomState"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomInfo",
        })
        if room_info.get("roomState"):
            if room_info.get("roomState") == "S":
                return True
            else:
                return False
        return None

    def set_gameStarted(self):
        update_rows(**{
            "table_name": "roomInfo",
            "columns": {
                "roomState": "S",
            },
            "filters": {
                "roomId": self.roomId,
            }
        })

    def distribute_cards(self):
        card = Card()
        cardsForPlayers = card.distribute_cards()
        for i,cards in enumerate(cardsForPlayers):
            cards = [str(card) for card in cards]
            update_rows(**{
                "table_name": "roomStatus",
                "columns": {
                    "cards": ",".join(cards),
                },
                "filters": {
                    "roomUserId": i,
                    "roomId": self.roomId,
                }
            })

    def get_cardsOfUser(self,userId):
        cursor = select_query(**{
            "columns": ["cards","roomUserId"],
            "filters": {
                "roomId": self.roomId,
                "userId": userId,
            },
            "table_name": "roomStatus",
        })
        x = cursor.fetchone()
        cards = x[0]
        cards = [int(i) for i in cards.split(",")]
        return cards

    def get_cardsOfAllUsers(self):
        cardsOfPlayers = {}
        for userId in self.players:
            cardsOfPlayers[userId] = self.get_cardsOfUser(userId)
        return cardsOfPlayers
