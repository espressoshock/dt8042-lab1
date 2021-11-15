##############################
### Task 2 : Main entry Point
#############################

## =IMPORTS
from Simulation import Simulation
from RandomAgent import RandomAgent
from Card import Card
from FixedAgent import FixedAgent
from ReflexAgent import ReflexAgent
from ReflexAgentMemory import ReflexAgentMemory


def main():
    p1 = RandomAgent()
    p2 = ReflexAgentMemory()
    sim = Simulation(player1=p1, player2=p2, hand_count=2, bid_count=3)
    sim.start()
    sim.show_results()


if __name__ == '__main__':
    main()
