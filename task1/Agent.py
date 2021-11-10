###########################
### Agent Class
##########################

# =IMPORTS
import math
from libs import vrepConst
from libs import vrep
import time


class Agent():
    #########################
    ### Constructor
    #########################
    def __init__(self, name: str, actuators: dict, sensors: dict, agentHandle: int, client: str, simulationDt: float, topSpeed: float, execModeSync: bool = True):
        self._agentHandle = agentHandle
        self._client = client
        self._actuators = actuators
        self._sensors = sensors
        self._execModeSync = execModeSync
        self._simDt = simulationDt
        self._topSpeed = topSpeed
        self._setTorque(topSpeed)

    #########################
    ### Methods to override
    #########################
    def act(self):
        pass

    #########################
    ### Steering Methods
    #########################
    # Ticks functionality only works for sync-mode
    # => simulation/render ticks/rate/interrupts
    # where tick @ interval sim.dt | n*dt
    ############################################

    ## forwards
    def driveForward(self, baseVelocity: float = 2, ticks: int = None):
        if ticks and self._execModeSync:
            for i in range(ticks):
                self._setMotorSpeed(baseVelocity, baseVelocity)
        else:
            self._setMotorSpeed(baseVelocity, baseVelocity)

    ## backwards
    def driveBackward(self, baseVelocity: float = 2, ticks: int = None):
        if ticks and self._execModeSync:
            for i in range(ticks):
                self._setMotorSpeed(-baseVelocity, -baseVelocity)
        else:
            self._setMotorSpeed(-baseVelocity, -baseVelocity)

    # ===========================
    # == Turn (Arc trajectory) ==
    # ===========================

    ## Left
    def driveLeft(self, baseVelocity: float = 2, ticks: int = None, turningStrength: float = 1.5):
        if ticks and self._execModeSync:
            for i in range(ticks):
                self._setMotorSpeed(
                    baseVelocity, baseVelocity + turningStrength)
        else:
            self._setMotorSpeed(baseVelocity, baseVelocity + turningStrength)

    ## Right
    def driveRight(self, baseVelocity: float = 2, ticks: int = None, turningStrength: float = 1.5):
        if ticks and self._execModeSync:
            for i in range(ticks):
                self._setMotorSpeed(
                    baseVelocity + turningStrength, baseVelocity)
        else:
            self._setMotorSpeed(baseVelocity + turningStrength, baseVelocity)

    ## Stop the motion
    # workaround for multi-args calls
    def driveBreak(self, *args):
        self._setMotorSpeed(0, 0)

    # ============================================
    # == Rotate (in-place / differential drive) ==
    # ============================================

    ## Spin Unclockwise
    def driveRotateUnclockwise(self, baseVelocity: float = 2, ticks: int = None):
        if ticks and self._execModeSync:
            for i in range(ticks):
                self._setMotorSpeed(
                    -baseVelocity, baseVelocity)
        else:
            self._setMotorSpeed(-baseVelocity, baseVelocity)

    ## Spin Clockwise
    def driveRotateClockwise(self, baseVelocity: float = 2, ticks: int = None):
        if ticks and self._execModeSync:
            for i in range(ticks):
                self._setMotorSpeed(
                    baseVelocity, -baseVelocity)
        else:
            self._setMotorSpeed(baseVelocity, -baseVelocity)

    ## drive in _direction_ for _time_ |DEPRECATED|
    def drive(self, direction: str = 'forward', velocity: float = 2, duration: float = 2.0):
        if direction not in ['forward', 'backward', 'left', 'right', 'spin']:
            direction = 'forward'
        start = time.time()
        getattr(self, 'drive'+direction.capitalize())(velocity)
        while time.time() < start + duration:
            pass
        self.driveBreak()

    #########################
    ### Utils
    #########################
    # Only for sync-mode
    # Convert: rate (ticks/interrupts) <-> time (ms)
    ############################################

    # rate -> ms
    def ticksToMs(self, ticks):
        return int(self._simDt * ticks)

    # ms -> ticks | ms has to be multiple of _simDT || int div
    def msToTicks(self, ms):
        return int(ms // self._simDt)

    #########################
    ### Privates
    #########################
    ## set motorSpeed (cmd sent together) of both wheels
    def _setMotorSpeed(self, leftMotorSpeed: float = 0, rightMotorSpeed: float = 0):
        if not self._execModeSync:
            # pause to transmit both commands
            vrep.simxPauseCommunication(self._client, 1)
        try:
            vrep.simxSetJointTargetVelocity(
                clientID=self._client,
                jointHandle=self._actuators['leftMotor'],
                targetVelocity=leftMotorSpeed,
                operationMode=vrepConst.simx_opmode_oneshot_wait
            )
            vrep.simxSetJointTargetVelocity(
                clientID=self._client,
                jointHandle=self._actuators['rightMotor'],
                targetVelocity=rightMotorSpeed,
                operationMode=vrepConst.simx_opmode_oneshot_wait
            )
        finally:
            if self._execModeSync:
                vrep.simxSynchronousTrigger(self._client)
            else:
                vrep.simxPauseCommunication(self._client, 0)  # resume
            # make sure sim.step is over
            vrep.simxGetPingTime(self._client)

    # set wheel torque to avoid slipping -> and preserve trajectory linearity
    def _setTorque(self, torque: float):
        try:
            vrep.simxSetJointForce(
                clientID=self._client,
                jointHandle=self._actuators['leftMotor'],
                force=torque,
                operationMode=vrepConst.simx_opmode_oneshot_wait
            )
            vrep.simxSetJointForce(
                clientID=self._client,
                jointHandle=self._actuators['rightMotor'],
                force=torque,
                operationMode=vrepConst.simx_opmode_oneshot_wait
            )
        finally:
            vrep.simxSynchronousTrigger(self._client)
            vrep.simxGetPingTime(self._client)

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
        return (agentPosition[2] / (2*math.pi))*360
        #return self.normalizeAngle(math.pi / 2 - agentPosition[2]) # deprecated

    #trigger render
    def triggerRender(self):
        vrep.simxSynchronousTrigger(self._client)
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
    def maxSpeed(self):
        return self._topSpeed

    @property
    def orientation(self):
        return self._getOrientation()

    @property
    def simulationDt(self):
        return self._simDt
