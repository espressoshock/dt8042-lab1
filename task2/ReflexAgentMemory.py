
###########################
### ReflexAgentMemory Class
##########################

# =IMPORTS
from Agent import Agent
from Hand import Hand


class ReflexAgentMemory(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self, name: str = 'Player 1'):
        super().__init__(name)
        self._memory = []  # opponent's hands after showdown

    #########################
    ### Deduce opponent's
    ### Agent
    #########################
    def deduce_opponent(self):
        def is_3_of_a_kind(hand):
            return hand[0] == hand[1] == hand[2]

        def is_one_pair(hand):
            return (hand[0] == hand[1] or
                    hand[0] == hand[2] or hand[1] == hand[2])

        # 0: random agent
        # 1: fixed agent
        # 2: reflex agent
        def _c_strategy(hand: Hand):
            if ((is_3_of_a_kind(hand.cards) and
                    (hand.bids[0] == hand.bids[1] == hand.bids[2] == 50)) or
                (is_one_pair(hand.cards) and
                    (hand.bids[0] == hand.bids[1] == hand.bids[2] == 25)) or
                (not (is_3_of_a_kind(hand.cards) and is_one_pair(hand.cards)) and
                    (hand.bids[0] == hand.bids[1] == hand.bids[2] == 10))):
                return 2
            if(hand.bids[0] == 10 and hand.bids[1] == 25 and hand.bids[2] == 50):
                return 1
            return 0

        # compare over time
        prev = _c_strategy(self._memory[0])
        for o_hand in self._memory:
            if _c_strategy(o_hand) != prev:
                return 0  # random
            prev = _c_strategy(o_hand)
        return prev

    #########################
    ### Override Bid
    #########################

    def bid(self, hand: int):
        if(len(self._memory) > 0):
            print('Decuded opponent is', self.deduce_opponent())
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

    #########################
    ### Memorize opponent's
    ### Approach
    #########################
    def memorize(self, hand: Hand):
        self._memory.append(hand)
