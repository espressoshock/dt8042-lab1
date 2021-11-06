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
        while time.time() < start + 10:
            print(sim._collectTargets())
            agent._setMotorSpeed(1, 1)
        agent._setMotorSpeed(0, 0)
        #time.sleep(2)

if __name__ == '__main__':
    main()
