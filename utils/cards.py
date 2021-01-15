import random

class Card():
    rankMapper = {
        0: 2,
        1: 3,
        2: 4,
        3: 5,
        4: 6,
        5: 7,
        6: 8,
        7: 9,
        8: 10,
        9: "J",
        10: "Q",
        11: "K",
        12: "A",
    }
    suitMapper = {
        5: "notrump",
        1: "spades",
        2: "diams",
        3: "hearts",
        4: "clubs",
    }

    pointMapper = {
        5: 12,
        1: 10,
        2: 8,
        3: 6,
        4: 4,
    }
    def __init__(self,listOfCards=None):
        self.totalNumberOfCards = 52
        self.totalNumberOfPlayers = 4
        self.numberOfCardsPerPlayer = int(
            self.totalNumberOfCards/self.totalNumberOfPlayers
        )
        self.numberOfCardsPerSuit = 13
        self.allCards = []
        self.shuffledCards = []
        if listOfCards is not None:
            self.allCards = listOfCards.copy()
            self.allCards.sort()


    def get_actualCard(self,cardId:int):
        suit = int(cardId / self.numberOfCardsPerSuit) + 1
        rank = cardId % self.numberOfCardsPerSuit
        return [self.suitMapper[suit],self.rankMapper[rank]]

    def map_intToCard(self):
        out = {}
        for cardId in self.allCards:
            out[cardId] = self.get_actualCard(cardId)
        return out

    def map_cardToDictDeck(self):
        card = self.map_intToCard()
        outDict = {
            "spades": {},
            "diams": {},
            "hearts": {},
            "clubs": {},
        }
        for i,acard in card.items():
            outDict[acard[0]][i] = acard[1]
        return outDict

    def shuffle_allCards(self):
        shuffledCards = list(range(self.totalNumberOfCards))
        random.shuffle(shuffledCards)
        self.shuffledCards = shuffledCards
        self.allCards = self.shuffledCards.copy()
        self.allCards.sort()

    def distribute_cards(self):
        return [self.shuffledCards[i*self.numberOfCardsPerPlayer:(i+1)*self.numberOfCardsPerPlayer] for i in range(4)]

    def convert_aCardToVisual(self,cardId):
        out = []
        out.append(self.suitMapper[int(cardId/self.numberOfCardsPerSuit)+1])
        out.append(self.rankMapper[cardId%self.numberOfCardsPerSuit])
        return out
