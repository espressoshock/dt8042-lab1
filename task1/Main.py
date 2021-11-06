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
        sim.start()

if __name__ == '__main__':
    main()
