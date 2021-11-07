###########################
### Agent Class
##########################

# =IMPORTS
import math
from ntpath import join
from libs import vrepConst
from libs import vrep
import time


class Agent():
    #########################
    ### Constructor
    #########################
    def __init__(self, name: str, actuators: dict, sensors: dict, agentHandle: int, client: str):
        self._agentHandle = agentHandle
        self._client = client
        self._actuators = actuators
        self._sensors = sensors

    #########################
    ### Methods to override
    #########################
    def act(self):
        pass

    #########################
    ### Steering Methods
    #########################
    ## forwards
    def driveForward(self, baseVelocity: float = 2):
        self._setMotorSpeed(baseVelocity, baseVelocity)

    ## backwards
    def driveBackward(self, baseVelocity: float = 2):
        self._setMotorSpeed(-baseVelocity, -baseVelocity)

    ## Left
    def driveLeft(self, baseVelocity: float = 2, turningRadius: float = 1.5):
        self._setMotorSpeed(baseVelocity, baseVelocity + turningRadius)

    ## Right
    def driveRight(self, baseVelocity: float = 2, turningRadius: float = 1.5):
        self._setMotorSpeed(baseVelocity + turningRadius, baseVelocity)
    
    ## Stop the motion
    def driveBreak(self):
        self._setMotorSpeed(0,0)
    
    ## drive in _direction_ for _time_
    def drive(self, direction: str = 'forward', velocity: float = 2, duration: float = 2.0):
        if direction not in ['forward', 'backward', 'left', 'right', 'spin']:
            direction = 'forward'
        start = time.time()
        getattr(self, 'drive'+direction.capitalize())(velocity)
        while time.time() < start + duration:
            pass
        self.driveBreak()

    ## Spin -> clockwise direction
    def driveSpin(self, baseVelocity: float = 1, turningAngle: float = 90):
        sAngle = self._getOrientation()
        if turningAngle < 0:
            self._setMotorSpeed(-baseVelocity, baseVelocity)
            correction = baseVelocity * 18 # need differential correction
            print('sAngle: ', self._getOrientation())
            print('target: ', sAngle + (-turningAngle))
            while self._getOrientation() <  (sAngle + (-turningAngle)) - correction:
                print('angle: ', self._getOrientation())
                pass
        else:
            self._setMotorSpeed(baseVelocity, -baseVelocity)
            correction = baseVelocity * 18 # need differential correction
            #print('sAngle: ', self._getOrientation())
            #print('target: ', sAngle + (-turningAngle))
            while self._getOrientation() >  (sAngle - turningAngle) + correction:
                print('angle: ', self._getOrientation())
                pass
        self.driveBreak()
        #print('final angle: ', self._getOrientation())

    #########################
    ### Privates
    #########################
    ## set motorSpeed (cmd sent together) of both wheels
    def _setMotorSpeed(self, leftMotorSpeed: float = 0, rightMotorSpeed: float = 0):
        # pause to transmit both commands
        vrep.simxPauseCommunication(self._client, 1)
        try:
            vrep.simxSetJointTargetVelocity(
                clientID=self._client,
                jointHandle=self._actuators['leftMotor'],
                targetVelocity=leftMotorSpeed,
                operationMode=vrepConst.simx_opmode_oneshot
            )
            vrep.simxSetJointTargetVelocity(
                clientID=self._client,
                jointHandle=self._actuators['rightMotor'],
                targetVelocity=rightMotorSpeed,
                operationMode=vrepConst.simx_opmode_oneshot
            )
        finally:
            vrep.simxPauseCommunication(self._client, 0)  # resume

    ## Get sensors data
    def _getSensorData(self, sensor: int):
        # get obstacle distance given sensor (handler)
        def _getObstacleDist(sensorHandler_):  # from original implementation
            # Get raw sensor readings using API
            # ref @ https://www.coppeliarobotics.com/helpFiles/en/b0RemoteApi-python.htm#simxReadProximitySensor
            rawSR = vrep.simxReadProximitySensor(
                self._client, sensorHandler_, vrepConst.simx_opmode_oneshot_wait)
            return {
                'detectionState': rawSR[1],
                'euclideanDistance': math.sqrt(rawSR[2][0]*rawSR[2][0] + rawSR[2][1]*rawSR[2][1] + rawSR[2][2]*rawSR[2][2]) if rawSR[1] == True
                else float('inf'),  # euclidean distance
                'rawDistance': rawSR[3],  # raw distance to detected point
                # The detected point relative to the sensor frame (ONLY FOR DEBUG)
                'detectedPointCoordinates': rawSR[2],
                # detected object handle (ONLY FOR DEBUG)
                # The normal vector of the detected surface, relative to the sensor frame (ONLY FOR DEBUG)
                'normalVectorDetectedSurface': rawSR[4]
            }
        #invalid sensor key
        if sensor not in self._sensors.values():
            return -1
        return _getObstacleDist(sensor)

    ## Get agent orientation
    def _getOrientation(self):
        retCode, agentPosition = vrep.simxGetObjectOrientation(
            self._client, self._agentHandle, -1, vrepConst.simx_opmode_oneshot_wait)
        return agentPosition[2] * 180 / math.pi
        #return self.normalizeAngle(math.pi / 2 - agentPosition[2]) # deprecated

    #################################
    ####### DEL ME #################
    #################################
    def normalizeAngle(self, angle: float):
        while angle > math.pi:
            angle -= 2*math.pi
        while angle < -math.pi:
            angle += 2*math.pi
        return angle

    #########################
    ### PROPS
    #########################
    @property
    def orientation(self):
        return self._getOrientation()
