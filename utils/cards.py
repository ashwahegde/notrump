import random

class Card():
    rankMapper = {
        0: 1,
        1: 2,
        2: 3,
        3: 4,
        4: 5,
        5: 6,
        6: 7,
        7: 8,
        8: 9,
        9: 10,
        10: 11,
        11: 12,
        12: 13,
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
            self.allCards.sort()
        else:
            self.shuffledCards = self.shuffle_allCards()
            self.allCards = self.shuffledCards

    def get_actualCard(self,cardId:int):
        suit = int(cardId / 13) + 1
        rank = cardId % 13
        return [self.suitMapper[suit],self.rankMapper[rank]]

    def map_intToCard(self):
        out = {}
        for cardId in self.allCards:
            out[cardId] = self.get_actualCard(cardId)
        return out

    def shuffle_allCards(self):
        shuffledCards = list(range(52))
        random.shuffle(shuffledCards)
        return shuffledCards

    def distribute_cards(self):
        return [self.shuffledCards[i*13:(i+1)*13] for i in range(4)]
