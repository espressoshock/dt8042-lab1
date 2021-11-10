###########################
### Task 1 : Main entry Point
##########################

## =IMPORTS
from Environment import Environment
from Simulation import Simulation


def main():
    with Simulation.init(port=19997, synchronous=True, fast=True) as sim:
        sim.start('fixed')


if __name__ == '__main__':
    main()
