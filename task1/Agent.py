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
    def __init__(self, client, vrep, actuators, sensors):
        self._actuators = actuators
        self._sensors = sensors
        self._client = client
        self._vrep = vrep
    
    #########################
    ### PROPS
    #########################
    ## All props here ##
    def turnLeft(self, velocity=1, duration=1):
        start = vrep.simxGetLastCmdTime(self._client)
        while vrep.simxGetLastCmdTime(self._client) < start + duration:
            print('turning...')
            print('time: ', vrep.simxGetLastCmdTime(self._client))
            self._setMotorSpeed('right', velocity)
            time.sleep(0.1)
        #stop all motors
        print("stopping...")
        self._stopMotors()


    #set motor speed
    def _setMotorSpeed(self, side='left', velocity=0):
        #check if side motor has been registered
        if side+'Motor' not in self._actuators:
            return -1
        try:
            vrep.simxPauseCommunication(self._client,True)
            vrep.simxSetJointTargetVelocity(self._client, self._actuators[side+'Motor'], velocity, vrepConst.simx_opmode_oneshot )
        finally:
            vrep.simxGetPingTime(self._client)
            self._vrep.simxPauseCommunication(self._client,False)
    #stop all motors helper function
    def _stopMotors(self):
        self._setMotorSpeed('left', 0)
        self._setMotorSpeed('right', 0)


    # Given sensor, fetch readings
    # return -> sensors.value if sensor present,
    # otherwise -> -1 
    def getSensorReading(self, sensor):
        print('sensor: ', sensor)
        print('Registered Sensors: ', self._sensors)
        #nested method
        def _getObstacleDist(sensorHandler_): #from original implementation
            # Get raw sensor readings using API
            rawSR = self._vrep.simxReadProximitySensor(self._client, sensorHandler_, vrepConst.simx_opmode_oneshot_wait)
            #print('rawsr', rawSR)
            # Calculate Euclidean distance
            if rawSR[1]: # if true, obstacle is within detection range, return distance to obstacle
                return math.sqrt(rawSR[2][0]*rawSR[2][0] + rawSR[2][1]*rawSR[2][1] + rawSR[2][2]*rawSR[2][2])
            else: # if false, obstacle out of detection range, return inf.
                return float('inf')

        #invalid sensor key
        if sensor not in self._sensors.values():
            return -1
        return _getObstacleDist(sensor)
    