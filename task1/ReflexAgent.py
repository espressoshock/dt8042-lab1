###########################
### ReflexAgent Class
##########################

from Agent import Agent
import math
from libs import vrep
from libs import vrepConst
import time


class ReflexAgent(Agent):
    #########################
    ### ALGO-CONSTANTS
    #########################
    TARGET_SELECTION_RANGE = 5
    DT_OFFSET = 30

    #########################
    ### Constructor
    #########################
    def __init__(self):
        super().__init__()
        self._cTarget = None  # current (selected) target

    # =======================
    # == Utils / Movements ==
    # =======================
    def _printTargetPool(self, targetPool):
        for target in targetPool:
            print(f'{target[1]}: {target[2]}, dir: {target[3]}')

    def _selectClosestTarget(self, offset: int = 0):
        targetPool = self.simulation.findTargets()
        print(f'closest target {targetPool[0][1], targetPool[0][0]}')
        print('closestTargetOFfset: ', offset)
        return targetPool[offset][0]  # target handle

    def _getRelativePosition(self, handle):
        relPos = vrep.simxGetObjectPosition(
            self._client, handle, self._agentHandle, vrepConst.simx_opmode_oneshot_wait)
        #print(f'x: {relPos[1][0]}, y: {relPos[1][1]}')
        return relPos

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

    def rotateUp(self):
        while self.orientation < 90 - self.DT_OFFSET:
            self.driveRotateUnclockwise(4)
        print('orient: ', self.orientation)

    def rotateDown(self):
        while self.orientation > -90 + self.DT_OFFSET:
            self.driveRotateClockwise(4)
        print('orient: ', self.orientation)

    # passed handle
    def _moveTowardsTargetOrtho(self, target):  # ortho approach
        x = self._getRelativePosition(target)[1][0]
        y = self._getRelativePosition(target)[1][1]
        #self.simulation.collectTargets()
        print(f'x: {x}, y: {y}')
        print(self._targetsCollected)
        print(target)
        if x >= 0:
            while abs(self._getRelativePosition(target)[1][0]) > 0.5:
                print('going forwards')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        else:
            while abs(self._getRelativePosition(target)[1][0]) > 0.5:
                print('going back')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=True) > 0:
                    return 1
                self.driveBackward(7)
        if y >= 0:
            self.rotateUp()
            while abs(self._getRelativePosition(target)[1][1]) > 0.5:
                print('going up')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        else:
            self.rotateDown()
            while abs(self._getRelativePosition(target)[1][1]) > 0.5:
                print('going down')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        print(self.simulation.collectTargets())
        return 0

    def _moveTowardsTargetArc(self, target):  # ortho approach
        x = self._getRelativePosition(target)[1][0]
        y = self._getRelativePosition(target)[1][1]
        #self.simulation.collectTargets()
        print(f'x: {x}, y: {y}')
        print(self._targetsCollected)
        print(target)
        if x >= 0:
            while abs(self._getRelativePosition(target)[1][0]) > 0.5:
                print('going forwards')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        else:
            while abs(self._getRelativePosition(target)[1][0]) > 0.5:
                print('going back')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=True) > 0:
                    return 1
                self.driveBackward(7)
        if y >= 0:
            #make the turn
            angleToGoal = math.atan2(y, x)
            roll, pitch, theta = self._getAgentPos()
            while abs(angleToGoal - self._getAgentPos()[2]) > 0.1:  # radians
                self.driveRotateClockwise(4)

            while abs(self._getRelativePosition(target)[1][1]) > 0.5:
                print('going up')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        else:
            #make turn
            while self.orientation > 90:  # check for y alignment
                self.driveRight(4)
            while abs(self._getRelativePosition(target)[1][1]) > 0.5:
                print('going down')
                if target in self._targetsCollected:
                    return 0
                self.simulation.collectTargets()
                if self._amIGonnaCrash(flipped=False) > 0:
                    return 1
                self.driveForward(7)
        print(self.simulation.collectTargets())
        return 0

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

    def tryOrientationFinder(self):
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

    def tryFollowWall(self):
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
            self.driveRotateUnclockwise(4)


        def followWall():
            self.driveForward(4)

            ## correction
            x = self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance']
            y = self._getSensorData(self._sensors['rightBackUltrasonic'])['euclideanDistance']
            print(x, y)
            if True:
                if x > 0.6: 
                    self.driveLeft(baseVelocity=4, turningStrength=2)
                if y > 0.6:
                    self.driveRight(baseVelocity=4, turningStrength=2)

                if x > y:
                    print('drive right')
                    self.driveRight(baseVelocity=4, turningStrength=2)
                else: #x > y
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
            }
            ## sensors
            d = 0.4
           # print('front', self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'])
            #print('frontL', self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'])
            #print('frontR', self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'])
            #print('SIDE: ', self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'])
            if self._getSensorData(self._sensors['rightFrontUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d:
                # case 0 / followint the wall
                print(f'{state_dict_[2]} SPECIAL CASE')
                return 2
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d:
                #case 1 / nothing
                print(f'{state_dict_[0]}')
                return 0
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d:
                # 'case 2 - front'
                print(f'{state_dict_[1]}')
                return 1
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d:
                # 'case 3 - fright'
                print(f'{state_dict_[2]}')
                return 2
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d:
                # 'case 4 - fleft'
                print(f'{state_dict_[0]}')
                return 0
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d:
                # 'case 5 - front and fright'
                print(f'{state_dict_[1]}')
                return 1
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] > d:
                # 'case 6 - front and fleft'
                print(f'{state_dict_[1]}')
                return 1
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d:
                # 'case 7 - front and fleft and fright'
                print(f'{state_dict_[1]}')
                return 1
            elif self._getSensorData(self._sensors['frontUltrasonic'])['euclideanDistance'] > d and self._getSensorData(self._sensors['frontLeftUltrasonic'])['euclideanDistance'] < d and self._getSensorData(self._sensors['frontRightUltrasonic'])['euclideanDistance'] < d:
                # 'case 8 - fleft and fright'
                print(f'{state_dict_[0]}')
                return 0
            else:
              print('uknown state')
              pass

        done = True

        ## main logic
        while done:
            state = readSensors()
            if state == 0:
                findWall()
            elif state == 1:
                turnLeft()
            elif state == 2:
                followWall()
            else:
                print('unknown state')

    #########################
    ### Override
    #########################

    def act(self):
        #self.tryOrientationFinder()
        self.tryFollowWall()
        
       
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
