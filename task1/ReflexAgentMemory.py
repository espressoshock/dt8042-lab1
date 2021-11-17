###########################
### ReflexAgentMemory Class
##########################

from Agent import Agent
import math
from libs import vrep
from libs import vrepConst
import time
from tqdm import tqdm
from colorama import Fore, Back, Style, init


class ReflexAgentMemory(Agent):
    #########################
    ### ALGO-CONSTANTS
    #########################
    TARGET_SELECTION_RANGE = 5
    DT_OFFSET = 30
    TARGET_DX_THRESHOLD = 0.1
    TARGET_DY_THRESHOLD = 0.1
    TARGET_SWITCH_THREASHOLD_RANGE = 2
    TRAVELLING_SPEED = 4
    FOLLOWING_WALL_SPEED = 4
    PRECISION_ROTATION_SPEED = 2
    FAST_ROTATION_SPEED = 4
    POINT_TO_ALLOWED_VARIATION = 0.1
    SIM_OFFSET_RAD = 0.2
    AGENT_TO_WALL_THREASHOLD_DISTANCE = 0.5
    AGENT_TO_INF_THREASHOLD_DISTANCE = 0.5
    AGENT_TO_WALL_SHIFT_CORRECTION_DISTANCE = 0.6
    AGENT_TO_WALL_SHIFT_CORRECTION_SPEED = 2
    AGENT_TO_WALL_SHIFT_CORRECTION_TURNING_STRENGTH = 8

    REFLEX_AGENT_STATES = {
        0: 'Idle',
        1: 'Moving to target',
        2: 'Looking for wall edge',
        3: 'Rotate left',
        4: 'Following wall edge',
        5: 'Rotate right'
    }

    # use memory to optimize
    # switching strategy
    # based on already visited nodes
    MEMORY = []

    #########################
    ### Constructor
    #########################
    def __init__(self):
        super().__init__()
        self._cTarget = None  # current (selected) target |deprecated|
        self._state = 0

    # =======================
    # == Utils / Movements ==
    # =======================

    def _printTargetPool(self, targetPool):
        for target in targetPool:
            print(f'{target[1]}: {target[2]}, dir: {target[3]}')

    def _selectClosestTarget(self, offset: int = 0):
        targetPool = self.simulation.findTargetsLeft()
        #print(f'closest target {targetPool[0][1], targetPool[0][0]}')
        #print('closestTargetOFfset: ', offset)
        return targetPool[offset][0]  # target handle

    def _getDirectionToTarget(self, handle):
        relPos = vrep.simxGetObjectPosition(
            self._client, handle, self._agentHandle, vrepConst.simx_opmode_oneshot_wait)
        #print(f'x: {relPos[1][0]}, y: {relPos[1][1]}')
        return relPos

    def log(self, action: str, type: str = 'Action'):
        if len(action) < 15:
            self.clearLog()
        print(
            f'{Back.BLUE} {type}  {Back.MAGENTA} {action}  {Style.RESET_ALL}', end='\r')

    def clearLog(self):
        print('\x1b[2K\r', end='\r')

    def updateVisitedList(self):
        for target in self.MEMORY:
            if target in self.targetsCollected:
                self.MEMORY.remove(target)

    # ======================
    # == Main Entry Point ==
    # ======================

    def _act(self):
        offset = 0  # start from first
        while len(self.targetsCollected) < len(self.simulation._env.targets)-1:
            ####################
            #    Perception    #
            ####################
            # (1) Find targets #
            #  Select closest  #
            ####################
            ct = self._selectClosestTarget(offset)
            ####################
            # (2) Try to move  #
            #  Towards target  #
            ####################
            offset = self._tryToMoveTowardsTarget(ct)
        time.sleep(2)

    # =============================
    # == (2) Move towards target ==
    # =============================

    def _tryToMoveTowardsTarget(self, target):
        self.updateVisitedList()
        #if target in self.MEMORY:
        #    self.log(type='Memory', action='Target already seen')
        #    return 1
        tx = self._getDirectionToTarget(target)[1][0]
        ty = self._getDirectionToTarget(target)[1][1]
        self.log(type='Target selected', action='Trying to move towards...')
        time.sleep(1)
        self.clearLog()
        if tx >= 0:
            while abs(self._getDirectionToTarget(target)[1][0]) > self.TARGET_DX_THRESHOLD:
                #check if you find a wall, then switch strategy
                if self.isWallAhead():
                    if self.followWall(target) == 0:
                        return 0
                    if self.followWall(target) == 1:
                        return 1
                self.log('Forward', 'Strategy')
                if target in self._targetsCollected:  # for convinience, might wanna replace this
                    return 0
                self.simulation.collectTargets(False, True)
                self.driveForward(self.TRAVELLING_SPEED)

        else:  # you can simplify this
            while abs(self._getDirectionToTarget(target)[1][0]) > self.TARGET_DX_THRESHOLD:
                #check if you find a wall, then switch strategy
                if self.isWallBehind():
                    break
                if self.isWallAhead():
                    if self.followWall(target) == 0:
                        return 0
                    if self.followWall(target) == 1:
                        return 1
                self.log('Backward', 'Strategy')
                if target in self._targetsCollected:  # for convinience, might wanna replace this
                    return 0
                self.simulation.collectTargets(False, True)
                self.driveBackward(self.TRAVELLING_SPEED)
        if ty >= 0:
            self.pointToTarget(target)
            while abs(self._getDirectionToTarget(target)[1][1]) > self.TARGET_DY_THRESHOLD:
                #check if you find a wall, then switch strategy
                if self.isWallAhead():
                    if self.followWall(target) == 0:
                        return 0
                    if self.followWall(target) == 1:
                        return 1
                self.log('Upward', 'Strategy')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets(False, True)
                self.driveForward(self.TRAVELLING_SPEED)
        else:
            self.pointToTarget(target)
            while abs(self._getDirectionToTarget(target)[1][1]) > self.TARGET_DY_THRESHOLD:
                #check if you find a wall, then switch strategy
                if self.isWallAhead():
                    if self.followWall(target) == 0:
                        return 0
                    if self.followWall(target) == 1:
                        return 1
                self.log('Downward', 'Strategy')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets(False, True)
                self.driveForward(self.TRAVELLING_SPEED)
        return 0  # next, no offset

    # =============================
    # == (2.1) Point to target   ==
    # =============================
    def pointToTarget(self, target):
        # target = self._selectClosestTarget(offset)
        self.log(type='Strategy', action='Point to Target')
        # to->direction
        x, y, _ = self.direction
        # euler orientation angles
        alpha, beta, gamma = self.orientation
        #target
        gx, gy, _ = self.gp(target)

        #rotation
        dx = gx - x
        dy = gy - y
        # destination angle-> atan(dy, dx)
        # python add do-while please
        while abs((math.atan2(dy, dx)) - gamma - self.SIM_OFFSET_RAD) > self.POINT_TO_ALLOWED_VARIATION:
            # rotate
            # improve this by integrating dx,dy
            self.driveRotateUnclockwise(self.PRECISION_ROTATION_SPEED)
            # recalculate rot-diff. on x,y
            dx = gx - x
            dy = gy - y
            # update current agent direction for integration
            x, y, _ = self.direction
            alpha, beta, gamma = self.orientation

    # ====================
    # == wall detection ==
    # ====================
    def isWallAhead(self):
        if (
                (
                    self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                    self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                    self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE)):
            return False
        else:
            return True

    def isWallBehind(self):
        if (self._getSensorData(self._sensors['backUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
            self._getSensorData(self._sensors['backLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                self._getSensorData(self._sensors['backRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
            return False
        else:
            return True

    # =======================
    # == (3) Wall folowing ==
    # =======================
    def followWall(self, target):
        self.MEMORY.append(target)


        def findWallEdge():
            #self.driveForward(self.FOLLOWING_WALL_SPEED)
            self.driveRight(baseVelocity=2, turningStrength=12)
            #self.driveBreak()

        def rotateLeft():
            self.driveRotateUnclockwise(self.FAST_ROTATION_SPEED)
            #self.driveBreak()

        def rotateRight():
            self.driveRight(baseVelocity=2, turningStrength=15)
            self.driveBreak()
            self.driveRotateClockwise(self.PRECISION_ROTATION_SPEED)
            self.driveBreak()

        def followWallEdge():
            self.driveForward(self.FOLLOWING_WALL_SPEED)

        def switchTarget():
            # new closest target
            ct = self._selectClosestTarget()
            ntx = self._getDirectionToTarget(ct)[1][0]
            nty = self._getDirectionToTarget(ct)[1][1]
            # current hold target
            ctx = self._getDirectionToTarget(target)[1][0]
            cty = self._getDirectionToTarget(target)[1][1]

            ntDistance = math.sqrt(ntx**2 + nty**2)
            ctDistance = math.sqrt(ctx**2 + cty**2)

            print('dist: ', ntDistance, ctDistance)
            print('memory', self.MEMORY)
            print('ctarget: ', target, ct)

            if ((ct != target) and (ntDistance < ctDistance) and (ntDistance < self.TARGET_SWITCH_THREASHOLD_RANGE)
            ):
                self.log(action='Target Change', type='Strategy')
                return ct
            return -1

        def alreadyVisited(_target):
            return _target in self.MEMORY

        def followWallEdge():
            self.driveForward(self.FOLLOWING_WALL_SPEED)

            # apply shift correction
            x = self._getSensorData(self._sensors['rightFrontUltrasonic'])[
                'euclideanDistance']
            y = self._getSensorData(self._sensors['rightBackUltrasonic'])[
                'euclideanDistance']
            if True:  # might wanna apply constraint here
                if x > self.AGENT_TO_WALL_SHIFT_CORRECTION_DISTANCE:
                    self.log(type='Correction Strategy', action='Shift Left')
                    self.driveLeft(baseVelocity=self.AGENT_TO_WALL_SHIFT_CORRECTION_SPEED,
                                   turningStrength=self.AGENT_TO_WALL_SHIFT_CORRECTION_TURNING_STRENGTH)
                if y > self.AGENT_TO_WALL_SHIFT_CORRECTION_DISTANCE:
                    self.log(type='Correction Strategy', action='Shift Right')
                    self.driveRight(baseVelocity=self.AGENT_TO_WALL_SHIFT_CORRECTION_SPEED,
                                    turningStrength=self.AGENT_TO_WALL_SHIFT_CORRECTION_TURNING_STRENGTH)

                if x > y:
                    self.log(type='Correction Strategy', action='Shift Right')
                    self.driveRight(baseVelocity=self.AGENT_TO_WALL_SHIFT_CORRECTION_SPEED,
                                    turningStrength=self.AGENT_TO_WALL_SHIFT_CORRECTION_TURNING_STRENGTH)
                else:  # x > y
                    self.log(type='Correction Strategy', action='Shift Left')
                    self.driveLeft(baseVelocity=self.AGENT_TO_WALL_SHIFT_CORRECTION_SPEED,
                                   turningStrength=self.AGENT_TO_WALL_SHIFT_CORRECTION_TURNING_STRENGTH)

        def readSensors():
            if (self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                    self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # special case 1 / following the wall
                self._state = 4
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['rightBackUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_INF_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_INF_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_INF_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_INF_THREASHOLD_DISTANCE):
                # special case 2 / turning around wall corner
                self._state = 5
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 1 / nothin
                self._state = 2
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 2 / front detection
                self._state = 3
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 3 / front-right detection
                self._state = 4
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 4 / front-left detection
                self._state = 2
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 5 / front and front-right detection
                self._state = 3
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 6 / front and front-left detection
                self._state = 3
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 7 / front and front-left and front-right detection
                self._state = 3
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < self.AGENT_TO_WALL_THREASHOLD_DISTANCE):
                # case 8 / front-left and front-right detection
                self._state = 2
                self.log(type='State Change',
                         action=self.REFLEX_AGENT_STATES[self._state])
                return self._state
            else:
                self.log(type='Error', action='Unhandled state')

        start = time.perf_counter()
        while target not in self.targetsCollected:

            #if not alreadyVisited() and switchTarget() == 1:
            #    return 1
            readSensors()
            self.simulation.collectTargets(False, True)
            if self._state == 2:
                if time.perf_counter() > start + 2:
                    return 0
                findWallEdge()
            elif self._state == 3:
                rotateLeft()
            elif self._state == 4:
                if switchTarget() != -1:
                    return 1
                followWallEdge()
            elif self._state == 5:
                rotateRight()
            else:
                self.log(type='State', action='Unknown state')

    # ================
    # == Algo Tests ==
    # ================

    def testMoveTowardsTargetOrtho(self, target):  # ortho approach
        x = self._getDirectionToTarget(target)[1][0]
        y = self._getDirectionToTarget(target)[1][1]
        #self.simulation.collectTargets()
        print(f'x: {x}, y: {y}')
        print(self._targetsCollected)
        print(target)
        if x >= 0:
            while abs(self._getDirectionToTarget(target)[1][0]) > 0.5:
                print('going forwards')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        else:
            while abs(self._getDirectionToTarget(target)[1][0]) > 0.5:
                print('going back')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=True) > 0:
                    return 1
                self.driveBackward(7)
        if y >= 0:
            self.rotateUp()
            while abs(self._getDirectionToTarget(target)[1][1]) > 0.5:
                print('going up')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        else:
            self.rotateDown()
            while abs(self._getDirectionToTarget(target)[1][1]) > 0.5:
                print('going down')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        print(self.simulation.collectTargets())
        return 0

    def _amIGonnaCrash(self, flipped: bool = False):
        if flipped:
            pass
        else:
            fusData1 = self._getSensorData(self._sensors['frontUltrasonic'])
            fusData2 = self._getSensorData(
                self._sensors['frontLeftUltrasonic'])
            fusData3 = self._getSensorData(
                self._sensors['frontRightUltrasonic'])
            print('DATA: ', fusData1['euclideanDistance'],
                  fusData2['euclideanDistance'], fusData3['euclideanDistance'])
            if fusData1['euclideanDistance'] < 0.2 and fusData2['euclideanDistance'] < 0.2 and fusData3['euclideanDistance'] < 0.2:
                return 1
        return 0

    def testOrientationFinder(self):
        tTargets = 1
        print(self._selectClosestTarget())
        offset = 3
        target = self._selectClosestTarget(offset)

        #x = self._getRelativePosition(target)[1][0]
        #y = self._getRelativePosition(target)[1][1]

        # robot
        x, y, _ = self._getAgentPos()
        roll, pitch, theta = self.go(self._agentHandle)
        #target
        gx, gy, gz = self.gp(target)

        #rotation
        incx = gx - x
        incy = gy - y
        angleToGoal = math.atan2(incy, incx)  # need quadrant => sign
        print(angleToGoal-theta)
        while abs(angleToGoal - theta) > 0.05:
            print('res; ', angleToGoal-theta)
            self.driveRotateUnclockwise(2)
            incx = gx - x
            incy = gy - y
            angleToGoal = math.atan2(incy, incx)
            x, y, _ = self._getAgentPos()
            roll, pitch, theta = self.go(self._agentHandle)
        print('end angle', angleToGoal-theta)

    def testFollowWall(self):
        def findWall():
            self.driveForward(4)
            #self.driveRotateClockwise(4)

        def turnLeftInPlace():
            roll, pitch, startT = self.go(self._agentHandle)
            print(startT)
            while self.go(self._agentHandle)[2] < startT + math.pi/2:
                roll, pitch, theta = self.go(self._agentHandle)
                print('theta: ', theta)
                self.driveRotateUnclockwise(2)
            print('end angle', theta)

        def turnLeft():
            roll, pitch, startT = self.go(self._agentHandle)
            #while self.go(self._agentHandle)[2] <
            self.driveRotateUnclockwise(5)

        def turnRight():
            roll, pitch, startT = self.go(self._agentHandle)
            #while self.go(self._agentHandle)[2] <
            self.driveRotateClockwise(5)

        def followWall():
            self.driveForward(4)

            ## correction
            x = self._getSensorData(self._sensors['rightFrontUltrasonic'])[
                'euclideanDistance']
            y = self._getSensorData(self._sensors['rightBackUltrasonic'])[
                'euclideanDistance']
            print(x, y)
            if True:
                if x > 0.6:
                    self.driveLeft(baseVelocity=4, turningStrength=2)
                if y > 0.6:
                    self.driveRight(baseVelocity=4, turningStrength=2)

                if x > y:
                    print('drive right')
                    self.driveRight(baseVelocity=4, turningStrength=2)
                else:  # x > y
                    print('drive left')
                    self.driveLeft(baseVelocity=4, turningStrength=2)
            '''
            if self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'] > 0.5:
                print('drive right')
                self.driveLeft(baseVelocity=4, turningStrength=2)
            else:
                print('drive left')
                self.driveLeft(baseVelocity=4, turningStrength=2)
            '''

        def readSensors():
            ##g-vars
            state_dict_ = {
                0: 'find the wall',
                1: 'turn left',
                2: 'follow wall',
                3: 'turn right'
            }
            ## sensors
            d = 0.4
            D = 0.4
           # print('front', self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'])
            #print('frontL', self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'])
            #print('frontR', self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'])
            #print('SIDE: ', self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'])
            if (self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'] < d and
                self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and
                self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and
                    self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d):
                # case 0 / followint the wall
                print(f'{state_dict_[2]} SPECIAL CASE 1')
                return 2
            elif (self._getSensorData(self._sensors['rightBackUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'] > D and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > D and
                  self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > D and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > D):
                print(f'{state_dict_[3]} SPECIAL CASE 2(3)')
                return 3
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d):
                #case 1 / nothing
                print(f'{state_dict_[0]}')
                return 0
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d):
                # 'case 2 - front'
                print(f'{state_dict_[1]}')
                return 1
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d):
                # 'case 3 - fright'
                print(f'{state_dict_[2]}')
                return 2
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d):
                # 'case 4 - fleft'
                print(f'{state_dict_[0]}')
                return 0
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d):
                # 'case 5 - front and fright'
                print(f'{state_dict_[1]}')
                return 1
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d):
                # 'case 6 - front and fleft'
                print(f'{state_dict_[1]}')
                return 1
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d):
                # 'case 7 - front and fleft and fright'
                print(f'{state_dict_[1]}')
                return 1
            elif (self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and
                  self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and
                  self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d):
                # 'case 8 - fleft and fright'
                print(f'{state_dict_[0]}')
                return 0
            else:
              print('uknown state')
              pass

        done = True

        ## main logic
        while done:
            self.simulation.collectTargets()  # just to test ->  to avoid collision
            state = readSensors()
            if state == 0:
                findWall()
            elif state == 1:
                turnLeft()
            elif state == 2:
                followWall()
            elif state == 3:
                turnRight()
            else:
                print('unknown state')

    def _getAgentPos(self):
        res, agentPos = vrep.simxGetObjectPosition(
            self._client, self._agentHandle, -1, vrepConst.simx_opmode_oneshot_wait)
        #print(f'x: {relPos[1][0]}, y: {relPos[1][1]}')
        return agentPos

    def _getAgentQuaternion(self):
        agentPos = vrep.simxGetObjectQuaternion(
            self._client, self._agentHandle, -1, vrepConst.simx_opmode_oneshot_wait)
        #print(f'x: {relPos[1][0]}, y: {relPos[1][1]}')
        return agentPos

    def gp(self, handle):
        res, pos = vrep.simxGetObjectPosition(
            self._client, handle, -1, vrepConst.simx_opmode_oneshot_wait)
        #print(f'x: {relPos[1][0]}, y: {relPos[1][1]}')
        return pos

    def go(self, handle):
        res, ori = vrep.simxGetObjectOrientation(
            self._client, handle, -1, vrepConst.simx_opmode_oneshot_wait)
        #print(f'x: {relPos[1][0]}, y: {relPos[1][1]}')
        return ori

    def rotateUp(self):
        while self.orientation < 90 - self.DT_OFFSET:
            self.driveRotateUnclockwise(4)
        print('orient: ', self.orientation)

    def rotateDown(self):
        while self.orientation > -90 + self.DT_OFFSET:
            self.driveRotateClockwise(4)
        print('orient: ', self.orientation)

    #########################
    ### Override
    #########################
    def act(self):
        #self.tryOrientationFinder()
        #self.testFollowWall()
        self._act()
        #self.pointToTarget(8)
        #self.followWall()

        '''
        while abs(angleToGoal - theta) > 0.05:
            print('res; ', angleToGoal-theta)
            self.driveRotateUnclockwise(2)
            #angleToGoal = math.atan2(incy, incx)
            roll, pitch, theta = self.go(self._agentHandle)
        print('end angle', angleToGoal-theta)
        '''

        '''
        print(f'x: {x}, y: {y}')
        print(self._targetsCollected)
        print(target)

        angleToGoal = math.atan2(y, x)
        roll, pitch, theta = self._getAgentPos()
        while abs(angleToGoal - theta) > 0.1: #radians
            print('agt: ', angleToGoal-theta)
            self.driveRotateUnclockwise(4)
            roll, pitch, theta = self._getAgentPos()

        '''
        '''
        while len(self.targetsCollected) < 10:
            ct = self._selectClosestTarget(offset)
            offset = self._moveTowardsTargetArc(ct)
        print('total collected targets: ', self.targetsCollected)
        time.sleep(2)
        '''
