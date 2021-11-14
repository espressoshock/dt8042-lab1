###########################
### FixedAgent Class
##########################

# =IMPORTS
from Agent import Agent
import Card


class FixedAgent(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self, name: str = 'Player 1'):
        super().__init__(name)

    #########################
    ### Override Bid
    #########################
    def bid(self, hand: int):
        bidded = self._hands[hand].bids
        if len(bidded) == 0:
            bid = 10
        if len(bidded) == 1:
            bid = 25
        if len(bidded) == 2:
            bid = 50
        self._hands[hand].add_bid(bid)
        return bid
