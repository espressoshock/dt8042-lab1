###########################
### FixedAgent Class
##########################

from Agent import Agent
import time
from libs import vrep


class FixedAgent(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self):
        super().__init__()

    #########################
    ### Movement-specifics
    #########################
    ONE_UNIT = 5.3  # vector uv @ 200ms tick-rate
    ROT_DT_ANGLE = 1.41
    ROT_SPEED = 1.76

    def _forward(self, unit: float = 1):
        cSimTime = 0
        while cSimTime < (self.ONE_UNIT/2.75) * unit:
            super().driveForward()
            cSimTime += self._simDt
        super().driveBreak()

    # Left / ortho-90deg
    def _rotateRight(self, baseVelocity: float = ROT_SPEED):
        cSimTime = 0
        while cSimTime < self.ROT_DT_ANGLE:
            self._setMotorSpeed(baseVelocity, -baseVelocity)
            cSimTime += self._simDt
        self._setMotorSpeed(0, 0)
        print('end angle: ', self._getOrientation())

    # Right / ortho-90deg
    def _rotateLeft(self, baseVelocity: float = ROT_SPEED):
        cSimTime = 0
        while cSimTime <= self.ROT_DT_ANGLE+0.15:
            self._setMotorSpeed(-baseVelocity, baseVelocity)
            cSimTime += self._simDt
        self._setMotorSpeed(0, 0)
        print('end angle: ', self._getOrientation())

    #########################
    ### override
    #########################

    def act(self):
        ######## PARAMS #######
        modules = [2, 2, 7.3, 1, 7.3, 1, 7.3, 7.3, 1, 7.3, 1, 7.3, 1, 7.3]
        ######## PARAMS #######

        #init zig-zag brute-force pattern
        self._rotateRight()
        self._forward(2)
        self._rotateLeft()
        self._forward(2.2)
        self._rotateLeft()
        self._forward(7.1)
        self._rotateRight()
        self._forward(1.2)
        self._rotateRight()
        self._forward(7.1)
        self._rotateLeft()
        self._forward(3)
        self._rotateLeft()
        self._forward(7.1)
        self._rotateRight()
        self._forward(2.4)
        self._rotateRight()
        self._forward(1.2)
        self._rotateLeft()
        self._forward(2.4)
        self._rotateLeft()
        self._forward(4*1.2)
        self._rotateLeft()
        self._forward(4*1)
        self._rotateLeft()
        self._forward(1.1)
        self._rotateLeft()
        self._forward(3*1.2)
        self._rotateRight()
        self._forward(2*1.2)
        self._rotateLeft()
        self._forward(7.1)


        '''
        self._rotateLeft()
        self._rotateLeft()
        self._forward(7.2)
        self._rotateLeft()
        self._forward(1.5)
        self._rotateLeft()
        self._forward(7.2)
        self._rotateRight()
        self._forward(1)
        self._rotateRight()
        self._forward(7.3)
        self._rotateLeft()
        self._forward(1)
        self._rotateLeft()
        self._forward(7.2)
        self._rotateRight()
        self._forward(1)
        self._rotateRight()
        self._forward(7.2)
        '''
    