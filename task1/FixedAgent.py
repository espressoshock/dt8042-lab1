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
        ROT_SPEED = self.maxSpeed
        TRAVELLING_SPEED = self.maxSpeed
        ORTHO_DT_TICKS = 21
        ORTHO_DT_TICKS_CORNER = 7 + ORTHO_DT_TICKS
        ######## PARAMS #######

        # ======================
        # == Zig-zag strategy ==
        # ======================

        self.driveRotateClockwise(ROT_SPEED, ORTHO_DT_TICKS)
        self.driveForward(TRAVELLING_SPEED, 30)
        self.driveRotateUnclockwise(ROT_SPEED, ORTHO_DT_TICKS_CORNER)
        self.driveForward(TRAVELLING_SPEED, 100)
