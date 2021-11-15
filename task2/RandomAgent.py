###########################
### RandomAgent Class
##########################

# =IMPORTS
from Agent import Agent
import random


class RandomAgent(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self, name: str = 'Player 1'):
        super().__init__(name)

    #########################
    ### Override Bid
    #########################
    def bid(self, hand: int, o_bid: int):
        bid = random.randint(1, 50)  # integer for convinience
        self._hands[hand].add_bid(bid)
        return bid
