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
        0: "notrump",
        1: "spades",
        2: "diams",
        3: "clubs",
        4: "hearts",
    }

    def __init__(self,listOfCards=None):
        if listOfCards:
            if not isinstance(listOfCards[0],int):
                listOfCards = [int(card) for card in listOfCards]
            self.allCards = listOfCards.copy()
        else:
            self.shuffledCards = self.shuffle_allCards()
            self.allCards = self.shuffledCards

    def get_actualCard(self,cardId:int):
        suit = int(cardId / 13) + 1
        rank = cardId % 13
        return [self.suitMapper[suit],self.rankMapper[rank]]

    def map_intToCard(self):
        out = {}
        self.allCards.sort()
        for cardId in self.allCards:
            out[cardId] = self.get_actualCard(cardId)
        return out

    def shuffle_allCards(self):
        shuffledCards = list(range(52))
        random.shuffle(shuffledCards)
        return shuffledCards

    def distribute_cards(self):
        return [self.shuffledCards[i*13:(i+1)*13] for i in range(4)]

    def convert_aCardToVisual(self,cardId):
        out = []
        out.append(self.suitMapper[int(cardId/13)+1])
        out.append(self.rankMapper[cardId%13])
        return out
