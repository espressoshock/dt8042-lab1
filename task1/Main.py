###########################
### Task 1 : Main entry Point
##########################

## =IMPORTS
from Environment import Environment
from Agent import Agent

import time

from Simulation import Simulation


def main():
    with Simulation.init() as sim:
        agent = sim.agent
        start = time.time()
        while time.time() < start + 2:
            agent._setMotorSpeed('left', 1)
        agent._setMotorSpeed('left', 0)

if __name__ == '__main__':
    main()
