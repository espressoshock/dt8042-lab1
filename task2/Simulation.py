###########################
### Simulation Class
##########################

# =IMPORTS
from Card import Card
from Agent import Agent
from Deck import Deck


class Simulation:
    #########################
    ### Constructor
    #########################
    def __init__(self, player1: Agent, player2: Agent, hand_count: int = 50, bid_count: int = 3):
        self._player1 = player1
        self._player2 = player2
        self._hand_count = hand_count
        self._bid_count = bid_count
        self._player1.set_hands_count(hand_count)
        self._player2.set_hands_count(hand_count)

    #########################
    ### Start / Game Flow ###
    #########################
    def start(self):

        for hand in range(self._hand_count):

            # ===========================
            # == Phase 1: Card Dealing ==
            # ===========================
            deck = Deck()
            deck.shuffle()

            # deal cards
            self._player1.receive_cards(deck.draw(3), hand)
            self._player2.receive_cards(deck.draw(3), hand)

            # ======================
            # == Phase 2: Bidding ==
            # ======================
            pot = 0
            print('bid count ', self._bid_count)
            for _ in range(self._bid_count):
                pot += self._player1.bid(hand)
                pot += self._player2.bid(hand)

            print('p1', self._player1.hands[hand].bids)
            print('p2', self._player2.hands[hand].bids)

            # =======================
            # == Phase 3: Showdown ==
            # =======================
            if self.compareHands(self._player1.show_cards(hand), self._player2.show_cards(hand)) == 2:
                self._player2.receive_winnings(pot, hand)
                self._player1.receive_winnings(0, hand)  # for convienience
            elif self.compareHands(self._player1.show_cards(hand), self._player2.show_cards(hand)) == 1:
                self._player1.receive_winnings(pot, hand)
                self._player2.receive_winnings(0, hand)
                self._player1.receive_winnings(0, hand)  # for convienience
            else:  # tie
                # N.D
                pass

    ####################
    ### Show results ###
    ####################
    def show_results(self):
        print(f'Results: ')
        print(f'Player 1 Statistics:')
        p1_totwinnings = p2_totwinnings = 0
        for i, hand in enumerate(self._player1.hands):
            print(f'# Hand N.{i}')
            print(f'\t Cards: {hand.cards}')
            print(f'\t Bids: {hand.bids}')
            print(f'\t Winnings: ', end='')
            for winning in hand.winnings:
                print(f'{winning}, ', end='')
                p1_totwinnings += winning
            print(f'\n-----------------------------------')
        print(f'Player 2 Statistics:')
        for i, hand in enumerate(self._player2.hands):
            print(f'# Hand N.{i}')
            print(f'\t Cards: {hand.cards}')
            print(f'\t Bids: {hand.bids}')
            print(f'\t Winnings: ', end='')
            for winning in hand.winnings:
                print(f'{winning}, ', end='')
                p2_totwinnings += winning
            print(f'\n-----------------------------------')
        print(f'Player 1 - Total winnings: {p1_totwinnings}')
        print(f'Player 1 - Total winnings: {p2_totwinnings}')
        print(
            f'Difference: {abs(p1_totwinnings-p2_totwinnings)} in favors of {"Player 1" if p1_totwinnings > p2_totwinnings else "Player 2"}')

    #########################
    ### Hand Comparison   ###
    #########################
    # 0: tie,
    # 1: hand1,
    # 2: hand2
    #########################
    def compareHands(self, hand1: list, hand2: list):
        def is_3_of_a_kind(hand):
            return hand[0].value == hand[1].value == hand[2].value

        def is_one_pair(hand):
            return (hand[0].value == hand[1].value or
                    hand[0].value == hand[2].value or hand[1] == hand[2].value)
        # different rank
        if is_3_of_a_kind(hand1) and not is_3_of_a_kind(hand2):
            return 1
        if not is_3_of_a_kind(hand1) and is_3_of_a_kind(hand2):
            return 2
        if is_one_pair(hand1) and not is_one_pair(hand2):
            return 1
        if not is_one_pair(hand1) and is_one_pair(hand2):
            return 2
        #same rank -> check values
        hand1.sort(reverse=True)
        hand2.sort(reverse=True)
        for i in range(len(hand1)):
            if hand1[i] < hand2[i]:
                return 2
            elif hand1[i] > hand2[i]:
                return 1
        return 0  # tie
