###########################
### RandomAgent Class
##########################

# =IMPORTS
from Agent import Agent
import random
from tqdm import tqdm
from colorama import Fore, Back, Style, init


class RandomAgent(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self):
        super().__init__()
        init()

    #########################
    ### Override
    #########################
    def act(self):
        ######## PARAMS #######
        strCSwitchPeriod = 3  # time period per strategy before switching
        simIters = 15  # sim. iterations
        ######## PARAMS #######

        piters = tqdm(range(simIters))
        for i in piters:
            name, action = self._randomAction()
            piters.set_description(
                f'{Back.BLUE} Action {Back.MAGENTA} {name}  {Style.RESET_ALL}')
            self.simulation.collectTargets(False, True)
            action(self.maxSpeed//2, self.msToTicks(strCSwitchPeriod))

    ## Get random action
    def _getRandomActionName(self):
        allowedActions = ['forward', 'backward',
                          'left', 'right', 'rotateUnclockwise', 'rotateClockwise', 'break']
        rAction = random.choice(allowedActions)
        return rAction[0].capitalize() + rAction[1:]

    ## execute random drive action / no args
    def _execRandomAction(self):
        rAction = self._getRandomAction()
        print(f'- Executing random action => [{rAction}]')
        getattr(super(), 'drive'+rAction)()

    ## get random drive action method
    def _randomAction(self):
        rAction = self._getRandomActionName()
        #print(f'- Executing random action => [{rAction}]')
        return (rAction, getattr(super(), 'drive'+rAction))
