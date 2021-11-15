###########################
### Deck Class
##########################

# =IMPORTS
import random
from typing import OrderedDict
from Card import Card


class Deck:
    ########################
    ### SUITS           ###
    ########################
    SUITS_ = {
        'c': ('clubs', '♣'),
        'd': ('diamonds', '♦'),
        'h': ('hearts', '♥'),
        's': ('spades', '♠')
    }
    VALUES = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'
    ]  # asc

    #########################
    ### Constructor
    #########################
    def __init__(self):
        self._suits = ['c', 'd', 'h', 's']
        self._cards = [Card(rank, suit)
                       for rank in self.VALUES for suit in self.SUITS_.keys()]

    #########################
    ### Shuffle
    #########################

    def shuffle(self):
        random.shuffle(self._cards)

    #########################
    ### Draw
    #########################
    def draw(self, n: int = 3):
        res = []
        for _ in range(n):
            res.append(self._cards.pop(0))
        return res
