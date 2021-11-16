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

    # =======================
    # == Movement Overload ==
    # =======================
    def rotateOrthoRightAndLog(self, logger, offset):
        for i in range(8+offset):
            self.simulation.collectTargets(False, True)
            self.execAndLog(logger, self._setMotorSpeed(
                self.maxSpeed//2, -self.maxSpeed//2), 'driveRotateClockwise')
            logger.update(1)

    def rotateOrthoLeftAndLog(self, logger, offset):
        for i in range(8+offset):
            self.simulation.collectTargets(False, True)
            self.execAndLog(logger, self._setMotorSpeed(-self.maxSpeed //
                            2, self.maxSpeed//2), 'driveRotateClockwise')
            logger.update(1)

    def driveForwardAndLog(self, logger, duration):
        for i in range(duration):
            self.simulation.collectTargets(False, True)
            self.execAndLog(logger, self._setMotorSpeed(
                self.maxSpeed//2, self.maxSpeed//2), 'driveForward')
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
        with tqdm(total=1322) as simIters:
            actions = [
                self.rotateOrthoRightAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 25),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 200),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 10),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 210),
                self.rotateOrthoRightAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 10),
                self.rotateOrthoRightAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 208),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 10),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 95),
                self.rotateOrthoRightAndLog(simIters, 0),  # 768 + (72)
                # around
                self.driveForwardAndLog(simIters, 30),
                self.rotateOrthoRightAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 47),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 62),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 57),
                self.rotateOrthoLeftAndLog(simIters, 1),
                self.driveForwardAndLog(simIters, 15),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 47),
                self.rotateOrthoRightAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 40),
                self.rotateOrthoRightAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 53),
                self.rotateOrthoLeftAndLog(simIters, 0),
                self.driveForwardAndLog(simIters, 50),  # 1169 + 72 + 72 + 9
            ]
            ## Execution action batch
            for action in actions:
                action
