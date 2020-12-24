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
        self.playersMapping = {}
        self.reversePlayerMappings = {}
        self.players = self.read_players()
        self.host = self.get_hostUserId()
        self.gameType = None
        self.cards = {}
        self.roomState = self.get_roomState()
        if self.is_gameStarted():
            self.cards = self.get_cardsOfAllUsers()
            self.gameType = self.get_gameType()
            if self.gameType:
                self.gameType = int(self.gameType)
            self.currentPlayer = self.get_currentStartPlayer()
            if not self.gameType:
                self.gameSelector = self.currentPlayer
                self.gameSelectorAlt = None
                if self.currentPlayer == self.get_firstPlayer():
                    self.gameSelectorAlt = self.get_teamMate(self.currentPlayer)
            else:
                pass

    def set_roomId(self,roomId):
        self.roomId = roomId

    def set_roomCode(self,roomCode):
        self.roomCode = roomCode

    def to_json(self):
        return self.__dict__

    def from_json(self,dicted_user):
        self.roomId = dicted_user.get("roomId")
        self.roomUserId = dicted_user.get("roomUserId")

    def is_player_valid(self,userId):
        if userId in self.players:
            return True
        else:
            return False

    def get_nextPlayer(self,userId):
        return self.players[(self.players.index(userId) + 1) % 4]

    def get_previousPlayer(self,userId):
        return self.players[(self.players.index(userId) - 1) % 4]

    def get_teamMate(self,userId):
        if not len(self.players) == 4:
            return None
        return self.players[(self.players.index(userId) + 2) % 4]

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
                },
                "table_name": "roomStatus"
            })
        except Exception as e:
            current_app.logger.error('failed to insert user to roomStatus')
            current_app.logger.error(f'{e}')

    def add_roomToGameStatus(self):
        insert_row(**{
            "columns": {
                "roomId": self.roomId,
                "starter": self.get_firstPlayer(),
            },
            "table_name": "gameStatus"
        })

    def remove_roomFromGameStatus(self):
        """use this funtion while cancelling the game."""
        delete_rows(**{
            "filter": {
                "roomId": self.roomId,
            },
            "table_name": "gameStatus"
        })

    def read_players(self):
        cursor = select_query(**{
            "columns": ["userId","roomUserId"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomStatus",
            "orderByAsc": "roomUserId",
        })
        players = []
        manyRow = cursor.fetchmany(4)
        if not manyRow:
            return []
        for arow in manyRow:
            players.append(arow[0])
            self.playersMapping[arow[1]] = arow[0]
            self.reversePlayerMappings[arow[0]] = arow[1]
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

    def get_roomState(self):
        cursor = select_query(**{
            "columns": ["roomState"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomInfo",
        })
        roomState = cursor.fetchone()
        if roomState:
            roomState = roomState[0]
            return roomState
        return None

    def is_gameStarted(self):
        if self.roomState == "S":
            return True
        else:
            return False

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

    def set_gameEnded(self):
        update_rows(**{
            "table_name": "roomInfo",
            "columns": {
                "roomState": "E",
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
                    "roomUserId": i+1,
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

    def set_gameType(self,gameType):
        update_rows(**{
            "table_name": "roomInfo",
            "columns": {
                "gameType": gameType,
            },
            "filters": {
                "roomId": self.roomId,
            }
        })
        self.gameType = gameType

    def get_gameType(self):
        cursor = select_query(**{
            "columns": ["gameType"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomInfo",
        })
        gameType = cursor.fetchone()
        if gameType:
            gameType = gameType[0]
            if gameType:
                return gameType
        return None

    def is_gameTypeSelected(self):
        if not self.gameType:
            return False
        return True

    def get_currentStartPlayer(self):
        cursor = select_query(**{
            "columns": ["starter"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "gameStatus",
        })
        currentStartPlayer = cursor.fetchone()
        if currentStartPlayer:
            currentStartPlayer = currentStartPlayer[0]
            if currentStartPlayer:
                return currentStartPlayer
        return None

    def get_firstPlayer(self):
        cursor = select_query(**{
            "columns": ["starter"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomInfo",
        })
        starterPlayer = cursor.fetchone()
        if starterPlayer:
            starterPlayer = starterPlayer[0]
            if starterPlayer:
                return starterPlayer
        return None

    def update_gameSelector(self,userId):
        update_rows(**{
            "table_name": "gameStatus",
            "columns": {
                "starter": userId,
            },
            "filters": {
                "roomId": self.roomId,
            }
        })

    def drop_game(self):
        update_rows(**{
            "table_name": "roomInfo",
            "columns": {
                "roomState": "C",
                "gameType": None,
            },
            "filters": {
                "roomId": self.roomId,
            }
        })
        self.update_gameSelector(self.get_previousPlayer(self.currentPlayer))

    def decide_winnerOfRound(self,roundStatus,firstPlayer):
        decisionCardType = int(roundStatus[firstPlayer] / 13) + 1
        bestCard = roundStatus[firstPlayer] % 13
        winner = firstPlayer
        roundStatus.pop(firstPlayer)
        if decisionCardType == self.gameType:
            isTrumpUsed = True
        else:
            isTrumpUsed = False
        if self.gameType == 0:
            for ithPlayer,cardId in roundStatus.items():
                if (int(cardId/13) + 1) == decisionCardType:
                    if cardId % 13 > bestCard:
                        bestCard = cardId % 13
                        winner = ithPlayer
        else:
            for ithPlayer,cardId in roundStatus.items():
                if isTrumpUsed:
                    if (int(cardId/13) + 1) == isTrumpUsed:
                        if cardId % 13 > bestCard:
                            bestCard = cardId % 13
                            winner = ithPlayer
                else:
                    if (int(cardId/13) + 1) == self.gameType:
                        isTrumpUsed = True
                        bestCard = cardId % 13
                        winner = ithPlayer
                    elif (int(cardId/13) + 1) == decisionCardType:
                        if cardId % 13 > bestCard:
                            bestCard = cardId % 13
                            winner = ithPlayer

        return winner

    def update_db_play_aCard(self,userId,cardId):
        update_rows(**{
            "table_name": "gameStatus",
            "columns": {
                "starter": self.get_nextPlayer(userId),
                f'player{self.reversePlayerMappings[userId]}': cardId,
            },
            "filters": {
                "roomId": self.roomId,
            }
        })
        cards = self.cards.get(userId)
        cards.remove(cardId)
        cards = [str(card) for card in cards]
        update_rows(**{
            "table_name": "roomStatus",
            "columns": {
                "cards": ",".join(cards),
            },
            "filters": {
                "roomId": self.roomId,
                "userId": userId,
            }
        })

    def clear_db_play_aCard(self,userId):
        """round is finished and winner is added, and other columns are cleared"""
        update_rows(**{
            "table_name": "gameStatus",
            "columns": {
                "starter": userId,
                "player1": None,
                "player2": None,
                "player3": None,
                "player4": None,
            },
            "filters": {
                "roomId": self.roomId,
            }
        })

    def give_PlayerAPoint(self,userId):
        cursor = select_query(**{
            "columns": ["points"],
            "filters": {
                "roomId": self.roomId,
                "userId": userId,
            },
            "table_name": "roomStatus",
        })
        point = cursor.fetchone()
        if not point:
            point = 0
        else:
            point = point[0]
            try:
                point = int(point)
            except:
                point = 0
        point += 1

        update_rows(**{
            "table_name": "roomStatus",
            "columns": {
                "points": point,
            },
            "filters": {
                "userId": userId,
                "roomId": self.roomId,
            }
        })

    def play_aCard(self,userId,cardId):
        """when someone plays a card"""
        playStatusDict = self.get_currentBufferCards()
        if len(playStatusDict) < 3:
            self.update_db_play_aCard(userId,cardId)
        else:
            #this is last player of the round
            winner = self.decide_winnerOfRound(
                playStatusDict,
                (self.reversePlayerMappings[userId]%4)+1,
            )
            self.clear_db_play_aCard(self.playersMapping[winner])
            self.give_PlayerAPoint(self.playersMapping[winner])

    def get_currentBufferCards(self):
        """get current cards played in the round"""
        cursor = select_query(**{
            "columns": ["player1","player2","player3","player4",],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "gameStatus",
        })
        out = {}
        currentBufferCards = cursor.fetchone()
        if currentBufferCards:
            for i,currentBufferCard in enumerate(currentBufferCards):
                if currentBufferCard or currentBufferCard==0:
                    out[i+1] = currentBufferCard
            return out
        else:
            return None

    def get_pointsTable(self):
        cursor = select_query(**{
            "columns": ["userId","points"],
            "filters": {
                "roomId": self.roomId,
            },
            "table_name": "roomStatus",
        })
        out = {}
        points = cursor.fetchmany(4)
        if not points:
            return None
        else:
            for userId,point in points:
                out[userId] = point
        return out
