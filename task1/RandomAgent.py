###########################
### RandomAgent Class
##########################

# =IMPORTS
from Agent import Agent
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
        strCSwitchPeriod = 2  # time period per strategy before switching
        simIters = 5  # sim. iterations
        ######## PARAMS #######

        for i in range(simIters):
            self._randomAction()(self.maxSpeed, self.msToTicks(strCSwitchPeriod))

    ## Get random action
    def _getRandomActionName(self):
        allowedActions = ['forward', 'backward',
                          'left', 'right', 'break']
        return (random.choice(allowedActions)).capitalize()

    ## execute random drive action / no args
    def _execRandomAction(self):
        rAction = self._getRandomAction()
        print(f'- Executing random action => [{rAction}]')
        getattr(super(), 'drive'+rAction)()

    ## get random drive action method
    def _randomAction(self):
        rAction = self._getRandomActionName()
        print(f'- Executing random action => [{rAction}]')
        return getattr(super(), 'drive'+rAction)
