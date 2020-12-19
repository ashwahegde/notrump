import random

class Card():
    def __init__(self,listOfCards=None):
        if listOfCards:
            self.allCards = listOfCards.copy()
            self.allCards.sort()
        else:
            self.shuffledCards = self.shuffle_cards()

    def map_intToCard(self):
        for eachCard in self.shuffledCards:
            pass

    def shuffle_cards(self):
        shuffledCards = list(range(52))
        random.shuffle(shuffledCards)
        return shuffledCards

    def distribute_cards(self):
        return [self.shuffledCards[i*13:(i+1)*13] for i in range(4)]
