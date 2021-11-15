###########################
### Card Class
##########################

# =IMPORTS

class Card:
    #########################
    ### Constructor
    #########################
    def __init__(self, value: int, suit: str):
        self._suit = suit
        self._value = value

    # ===================
    # == Comparison OP ==
    # ===================
    def __lt__(self, other):
        from Deck import Deck
        return Deck.VALUES.index(str(self._value)) < Deck.VALUES.index(str(other._value))

    def __gt__(self, other):
        from Deck import Deck
        return Deck.VALUES.index(str(self._value)) > Deck.VALUES.index(str(other._value))

    def __eq__(self, other):
       return self._value == other._value

    # ====================
    # == Representation ==
    # ====================
    def __str__(self):
        from Deck import Deck
        return str(self._value) + Deck.SUITS_[self._suit][1]

    def __repr__(self):
        from Deck import Deck
        return str(self._value) + Deck.SUITS_[self._suit][1]

    #V########################
    ### Props
    #########################
    @property
    def suit(self):
        return self._suit

    @property
    def value(self):
        return self._value
