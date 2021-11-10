################################
### FixedAgent Class
################################

from Agent import Agent
import time


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

        self.driveRotateClockwise(ROT_SPEED, ORTHO_DT_TICKS)
        self.driveForward(TRAVELLING_SPEED, 25)
        self.driveRotateUnclockwise(ROT_SPEED, ORTHO_DT_TICKS_CORNER)
        self.driveForward(TRAVELLING_SPEED, 50)
