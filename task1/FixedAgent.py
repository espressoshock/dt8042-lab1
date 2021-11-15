################################
### FixedAgent Class
################################

from Agent import Agent
import time
from tqdm import tqdm
from colorama import Fore, Back, Style, init


class FixedAgent(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self):
        super().__init__()

    # =======================
    # == Utils / Movements ==
    # =======================
    # prevent drift from fast change of direction
    def cancelDrift(self):
        self._setTorque(0)
        time.sleep(4)
        self._setTorque(0.5)
    
    def execAndLog(self, logger, action, actionName):
        logger.set_description(
            f'{Back.BLUE} Action {Back.MAGENTA} {actionName}  {Style.RESET_ALL}')
        action
        logger.update(1)


    #########################
    ### override
    #########################
    def act(self):
        ######## PARAMS #######
        ROT_SPEED = int(self.maxSpeed//2)
        TRAVELLING_SPEED = int(self.maxSpeed//2)
        ORTHO_DT_TICKS = 10
        ORTHO_DT_TICKS_CORNER = ORTHO_DT_TICKS
        ######## PARAMS #######

        # ======================
        # == Zig-zag strategy ==
        # ======================
        
        with tqdm(total=4) as simIters:
            self.execAndLog(simIters, self.driveRotateClockwise(ROT_SPEED, ORTHO_DT_TICKS), 'driveRotateClockwise')
            self.execAndLog(simIters, self.driveForward(TRAVELLING_SPEED, 25), 'driveForward')
            self.execAndLog(simIters, self.driveRotateUnclockwise(ROT_SPEED, ORTHO_DT_TICKS_CORNER), 'driveRotateUnclockwise')
            self.execAndLog(simIters, self.driveForward(TRAVELLING_SPEED, 50), 'driveForward')

