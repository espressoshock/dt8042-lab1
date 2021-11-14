###########################
### Agent Class
##########################

# =IMPORTS
from Card import Card
from Hand import Hand


class Agent:
    #########################
    ### Constructor
    #########################
    def __init__(self, name: str = 'Player 1'):
        self._name = name
        self._hands = []

    #########################
    ### Set hand size
    #########################
    def set_hands_count(self, count: int = 50):
        self._hands = [Hand() for _ in range(count)]

    #########################
    ### Receive Cards
    #########################
    def receive_cards(self, cards: list, hand: int):
        self._hands[hand].cards = cards  # property

    #########################
    ### Receive Winnings
    #########################
    def receive_winnings(self, winnings: float, hand: int):
        self._hands[hand].add_winnings(winnings)

    #########################
    ### Bid
    #########################
    def bid(self):
        pass

    #########################
    ### Show hand
    #########################
    def show_cards(self, hand: int):
        return self._hands[hand].cards

    #V########################
    ### Props
    #########################
    @property
    def hands(self):
        return self._hands
