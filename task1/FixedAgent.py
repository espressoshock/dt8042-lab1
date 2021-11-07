###########################
### FixedAgent Class
##########################

from Agent import Agent
import time


class FixedAgent(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self):
        super().__init__()

    #########################
    ### Override
    #########################
    def act(self):
        ######## PARAMS #######
        simDuration = 3*5  # sim.duration
        strCSwitchPeriod = 3  # time period per strategy before switching
        ######## PARAMS #######
        super().driveSpin(1, 90)  # change the driveSpin impl
        super().drive('forwards', 1, 1)
        super().driveSpin(1, -90)  # change the driveSpin impl
        super().drive('forwards', 1.5, 1)
        super().driveSpin(1, -90)  # change the driveSpin impl
        super().drive('forwards', 2, 3)
        super().driveSpin(1, 90)  # change the driveSpin impl
        super().drive('forwards', 0.5, 1)
        super().driveSpin(1, 90)  # change the driveSpin impl
        super().drive('forwards', 2, 3)
