###########################
### RandomAgent Class
##########################

from Agent import Agent
import random, time


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
        simDuration = 10 # sim.duration
        strCSwitchPeriod = 10  # time period per strategy before switching
        ######## PARAMS #######
        for i in range(simDuration):
            action = self._randomAction()
            cSimTime = 0
            while cSimTime < strCSwitchPeriod:
                action()
                cSimTime += self._simDt
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
    
    ## get random drive action method
    def _randomAction(self):
        rAction = self._getRandomAction()
        print(f'- Executing random action => [{rAction}]')
        return getattr(super(), 'drive'+rAction)
