###########################
### RandomAgent Class
##########################

from Agent import Agent
import time
import random


class RandomAgent(Agent):
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
        simDuration = 3*10 # sim.duration
        strCSwitchPeriod = 3  # time period per strategy before switching
        ######## PARAMS #######
        simStart = time.time()
        while time.time() < simStart + simDuration:
            self._execRandomAction()
            time.sleep(strCSwitchPeriod)
        super().driveBreak()

    ## Get random action
    def _getRandomAction(self):
        allowedActions = ['forward', 'backward',
                          'left', 'right', 'spinUnsupervised', 'break']
        return (random.choice(allowedActions)).capitalize()

    ## execute random drive action
    def _execRandomAction(self):
        rAction = self._getRandomAction()
        print(f'- Executing random action => [{rAction}]')
        getattr(super(), 'drive'+rAction)()
