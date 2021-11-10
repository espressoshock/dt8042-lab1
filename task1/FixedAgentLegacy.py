################################
### FixedAgent Class | LEGACY |
################################
# Pleas use non-legacy version
################################

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

    # ==============================
    # == Synchronous Impl.Example ==
    # ==============================

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

    # =================================
    # == Asynchronous Implementation ==
    # =================================

    ROT_SPEED_ASYNC = 2
    ROT_DT_ANGLE_ASYNC = 610  # iters ticks => based on server sim.dt
    ONE_UNIT_ASYNC = 1.5 # vector uv @ dt=10

    ##################################################################
    # custom dt of 10ms
    #Calculate updates in terms of ticks based on simulation Dt
    def _getDTTicks(self, rotDtAngleAsync: float = ROT_DT_ANGLE_ASYNC):
        return self.simulationDt * rotDtAngleAsync
    ##################################################################

    # Movements
    # -------------------------- #

    # Forward
    def _forwardAsync(self, unit: float = 1, baseVelocity: float = ROT_SPEED_ASYNC):
        start = time.perf_counter()
        while time.perf_counter() < start + unit * self.ONE_UNIT_ASYNC:
            #self.driveRotateUnclockwise(baseVelocity)
            self._setMotorSpeed(baseVelocity, baseVelocity)
        self._setMotorSpeed(0, 0)

    # Left / ortho-90deg
    def _rotateLeftAsync(self, baseVelocity: float = ROT_SPEED_ASYNC):
        start = time.perf_counter()
        print('Start angle: ', self.orientation)
        print('simDT: ', self.simulationDt)
        print('start, ', start)
        while time.perf_counter() < start + 1.1: #self._getDTTicks():
            print('Moving with angle: ', self.orientation)
            #self.driveRotateUnclockwise(baseVelocity)
            self._setMotorSpeed(-baseVelocity, baseVelocity)

        self._setMotorSpeed(0, 0)
        print('end angle', self.orientation)
        time.sleep(1)
    
    # Right / ortho-90deg
    def _rotateRightAsync(self, baseVelocity: float = ROT_SPEED_ASYNC):
        start = time.perf_counter()
        print('Start angle: ', self.orientation)
        print('simDT: ', self.simulationDt)
        print('start, ', start)
        while time.perf_counter() < start + 1.1: #self._getDTTicks():
            print('Moving with angle: ', self.orientation)
            #self.driveRotateUnclockwise(baseVelocity)
            self._setMotorSpeed(baseVelocity, -baseVelocity)

        self._setMotorSpeed(0, 0)
        print('end angle', self.orientation)
        time.sleep(1)
    

    #########################
    ### override
    #########################
    def act(self):
        ######## PARAMS #######
        modules = [2, 2, 7.3, 1, 7.3, 1, 7.3, 7.3, 1, 7.3, 1, 7.3, 1, 7.3]
        ######## PARAMS #######

        #init zig-zag brute-force pattern
        if self._execModeSync:
            self._rotateRight()
            self._forward(2)
            self._rotateLeft()
            self._forward(2.2)
            self._rotateLeft()
            self._forward(7.1)
            self._rotateRight()
            self._forward(1.2)#
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
        else:
            self._rotateRightAsync()
            self._forwardAsync(2)
            self._rotateLeftAsync()
            self._forwardAsync(2.2)
            self._rotateLeftAsync()
            self._forwardAsync(7.1)
            self._rotateRightAsync()
            self._forwardAsync(1)
            
