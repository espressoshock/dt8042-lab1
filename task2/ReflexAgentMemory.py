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
    def bid(self, hand: int, o_bid: int):
        # ===========
        # == Utils ==
        # ===========
        def is_3_of_a_kind(hand):
            return hand[0] == hand[1] == hand[2]

        def is_one_pair(hand):
            return (hand[0] == hand[1] or
                    hand[0] == hand[2] or hand[1] == hand[2])

        def default_strategy(cards: list):
            #on specific ranks
            if cards[0] == cards[1] == cards[2]:
                bid = 50
            elif cards[0] == cards[1] or cards[0] == cards[2] or cards[1] == cards[2]:
                bid = 25
            else:
                bid = 10
            return bid

        # =====================
        # == Deduce opponent ==
        # =====================
        bid = 0
        if(len(self._memory) > 0):
            print('Deduced opponent is', self.deduce_opponent())
            if self.deduce_opponent() == 0:
                bid = default_strategy(self._hands[hand].cards)
            elif self.deduce_opponent() == 1:
                bid = default_strategy(self._hands[hand].cards)
            elif self.deduce_opponent() == 2:
                if o_bid == 50:  # 3 of a kind
                    if is_3_of_a_kind(self.hands[hand].cards):
                        bid = 25  # do further opt based on card values
                    else:
                        bid = 0
                elif o_bid == 25:  # one pair
                    if is_3_of_a_kind(self.hands[hand].cards):
                        bid = 50
                    if is_one_pair(self.hands[hand].cards):
                        bid = 25  # do further opt based on card values
                    else:
                        bid = 0
                elif o_bid == 10:  # high card
                    if (is_3_of_a_kind(self.hands[hand].cards) or is_one_pair(self.hands[hand].cards)):
                        bid = 50
                    else:  # high card
                        bid = 25  # check of highest rank
        else:  # first round cannot deduce
            bid = default_strategy(self._hands[hand].cards)

        # =========
        # == Bid ==
        # =========
        self._hands[hand].add_bid(bid)
        return bid

    #########################
    ### Memorize opponent's
    ### Approach
    #########################
    def memorize(self, hand: Hand):
        self._memory.append(hand)
