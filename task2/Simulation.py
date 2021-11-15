###########################
### Simulation Class
##########################

# =IMPORTS
from Card import Card
from Agent import Agent
from Deck import Deck
from ReflexAgentMemory import ReflexAgentMemory

from colorama import Fore, Back, Style, init
from tqdm import tqdm
import time


class Simulation:
    #########################
    ### Constructor
    #########################
    def __init__(self, player1: Agent, player2: Agent, hand_count: int = 50, bid_count: int = 3):
        self._player1 = player1 if not isinstance(
            player1, ReflexAgentMemory) else player2
        self._player2 = player2 if (isinstance(
            player2, ReflexAgentMemory) and not isinstance(player1, ReflexAgentMemory)) else player1
        self._hand_count = hand_count
        self._bid_count = bid_count
        self._player1.set_hands_count(hand_count)
        self._player2.set_hands_count(hand_count)
        init()  # init colorama

    #########################
    ### Start / Game Flow ###
    #########################
    def start(self):

        print(
            f'{Back.YELLOW}{Fore.BLACK}  Simulation {Back.GREEN} Started  {Style.RESET_ALL} \n')
        # Track Progress
        hand_pool = tqdm(range(self._hand_count))
        for hand in hand_pool:

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
            for _ in range(self._bid_count):
                p1_bid = self._player1.bid(hand, 0)
                p2_bid = self._player2.bid(hand, p1_bid)
                pot += p1_bid + p2_bid

            # =======================
            # == Phase 3: Showdown ==
            # =======================
            if self.compareHands(self._player1.show_cards(hand), self._player2.show_cards(hand)) == 2:
                self._player2.receive_winnings(pot, hand)
                self._player1.receive_winnings(0, hand)  # for convienience
            elif self.compareHands(self._player1.show_cards(hand), self._player2.show_cards(hand)) == 1:
                self._player1.receive_winnings(pot, hand)
                self._player2.receive_winnings(0, hand)
            else:  # tie
                # N.D
                pass

            ## memorization
            if isinstance(self._player1, ReflexAgentMemory):
                self._player1.memorize(self._player2.hands[hand])
            if isinstance(self._player2, ReflexAgentMemory):
                self._player2.memorize(self._player1.hands[hand])

            # for visualization only
            time.sleep(0.01)
            hand_pool.set_description(f'Simulating Hand [{hand+1}]')
        print(
            f'\n{Back.YELLOW}{Fore.BLACK}  Simulation {Back.GREEN} Finished  {Style.RESET_ALL} \n')

    ####################
    ### Show results ###
    ####################
    def show_results(self, slowdown: bool = False):
        print(f'Results: ')
        if slowdown:
            p1_totwinnings = p2_totwinnings = 0
            # len -> player1.hands == player2.hands
            for i in range(len(self._player1.hands)):
                #player1
                print(f'{Back.WHITE}{Fore.BLACK}Hand N.{i}  {Style.RESET_ALL}\n')
                print(f'\t{Back.CYAN} Player 1: {Style.RESET_ALL}')
                print(
                    f'\t\t {Fore.YELLOW}Cards: {Style.RESET_ALL}{self._player1.hands[i].cards}')
                print(
                    f'\t\t {Fore.LIGHTRED_EX}Bids: {Style.RESET_ALL}{self._player1.hands[i].bids}')
                print(
                    f'\t\t {Fore.GREEN}Winnings: {Style.RESET_ALL} {self._player1.hands[i].winnings[0]}')
                #player2
                print(f'\t{Back.MAGENTA} Player 2: {Style.RESET_ALL}')
                print(
                    f'\t\t {Fore.YELLOW}Cards: {Style.RESET_ALL}{self._player2.hands[i].cards}')
                print(
                    f'\t\t {Fore.LIGHTRED_EX}Bids: {Style.RESET_ALL}{self._player2.hands[i].bids}')
                print(
                    f'\t\t {Fore.GREEN}Winnings: {Style.RESET_ALL} {self._player2.hands[i].winnings[0]}')
                print(f'\n-----------------------------------\n')
                p1_totwinnings += self._player1.hands[i].winnings[0]
                p2_totwinnings += self._player2.hands[i].winnings[0]
                time.sleep(0.1)
            print(
                f'{Back.CYAN}Player 1 {Style.RESET_ALL} Total winnings: {p1_totwinnings}')
            print(
                f'{Back.MAGENTA} Player 2 {Style.RESET_ALL} Total winnings: {p2_totwinnings}')
            print(
                f'Difference: {abs(p1_totwinnings-p2_totwinnings)} in favors of {"Player 1" if p1_totwinnings > p2_totwinnings else "Player 2"}')
            if isinstance(self._player2, ReflexAgentMemory):
                print(
                    f'{Back.LIGHTYELLOW_EX}{Fore.BLACK}  Deduced opponent: {Back.GREEN}  {self._player2.AGENTS_[self._player2.deduce_opponent()]} Agent {Style.RESET_ALL}')

        else:
            print(f'{Back.CYAN} Player 1 Statistics: {Style.RESET_ALL}')
            p1_totwinnings = p2_totwinnings = 0
            for i, hand in enumerate(self._player1.hands):
                print(f'{Back.WHITE}{Fore.BLACK}Hand N.{i}  {Style.RESET_ALL}')
                print(f'\t {Fore.YELLOW}Cards: {Style.RESET_ALL}{hand.cards}')
                print(f'\t {Fore.LIGHTRED_EX}Bids: {Style.RESET_ALL}{hand.bids}')
                print(f'\t {Fore.GREEN}Winnings: {Style.RESET_ALL}', end='')
                for winning in hand.winnings:
                    print(f'{winning}, ', end='')
                    p1_totwinnings += winning
                print(f'\n-----------------------------------')
            print(f'{Back.MAGENTA} Player 2 Statistics: {Style.RESET_ALL}')
            for i, hand in enumerate(self._player2.hands):
                print(f'{Back.WHITE}{Fore.BLACK}Hand N.{i}  {Style.RESET_ALL}')
                print(f'\t {Fore.YELLOW}Cards: {Style.RESET_ALL}{hand.cards}')
                print(f'\t {Fore.LIGHTRED_EX}Bids: {Style.RESET_ALL}{hand.bids}')
                print(f'\t {Fore.GREEN}Winnings: {Style.RESET_ALL}', end='')
                for winning in hand.winnings:
                    print(f'{winning}, ', end='')
                    p2_totwinnings += winning
                print(f'\n-----------------------------------')
            print(
                f'{Back.CYAN}Player 1 {Style.RESET_ALL} Total winnings: {p1_totwinnings}')
            print(
                f'{Back.MAGENTA} Player 2 {Style.RESET_ALL} Total winnings: {p2_totwinnings}')
            print(
                f'Difference: {abs(p1_totwinnings-p2_totwinnings)} in favors of {"Player 1" if p1_totwinnings > p2_totwinnings else "Player 2"}')
            if isinstance(self._player2, ReflexAgentMemory):
                print(
                    f'{Back.LIGHTYELLOW_EX}{Fore.BLACK}  Deduced opponent: {Back.GREEN}  {self._player2.AGENTS_[self._player2.deduce_opponent()]} Agent {Style.RESET_ALL}')

    #########################
    ### Hand Comparison   ###
    #########################
    # 0: tie,
    # 1: hand1,
    # 2: hand2
    #########################
    def compareHands(self, hand1: list, hand2: list):
        def is_3_of_a_kind(hand):
            return hand[0] == hand[1] == hand[2]

        def is_one_pair(hand):
            return (hand[0] == hand[1] or
                    hand[0] == hand[2] or hand[1] == hand[2])
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
