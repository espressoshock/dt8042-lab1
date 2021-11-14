
###########################
### Hand Class / Round
##########################

# =IMPORTS

class Hand:
    #########################
    ### Constructor
    #########################
    def __init__(self, cards: list = [], bids: list = [], winnings: list = []):
        self._cards = cards
        self._bids = []
        self._winnings = []

    #########################
    ### Add bid
    #########################
    def add_bid(self, bid):
        self._bids.append(bid)

    #########################
    ### Add Winning
    #########################
    def add_winnings(self, winning):
        self._winnings.append(winning)

    #########################
    ### Props
    #########################
    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, value):
        self._cards = value

    @property
    def bids(self):
        return self._bids

    @property
    def winnings(self):
        return self._winnings

    @winnings.setter
    def winnings(self, value):
        self._winnings = value
