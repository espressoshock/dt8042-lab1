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
        #on specific card combinations
        '''
        if set([Card('Q', 's'), Card('5', 's'), Card('4', 's')]).issubset(cards):
            return bid - 10
        '''
        # ===================
        # == Bidded amount ==
        # ===================
        bidded = self._hands[hand].bids
        cards = self._hands[hand].cards
        #on specific ranks
        if cards[0] == cards[1] == cards[2]:
            bid = 50
        elif cards[0] == cards[1] or cards[0] == cards[2] or cards[1] == cards[2]:
            bid = 25
        else:
            bid = 10
        self._hands[hand].add_bid(bid)
        return bid
