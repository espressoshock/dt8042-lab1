###########################
### Agent Class
##########################

# =IMPORTS
import math
from libs import vrepConst

class Agent():
    #########################
    ### Constructor
    #########################
    def __init__(self, client, vrep, actuators, sensors):
        self.actuators = actuators
        self.sensors = sensors
        self.client = client
        self.vrep = vrep

    # Given sensor, fetch readings
    # return -> sensors.value if sensor present,
    # otherwise -> -1 
    def getSensorReading(self, sensor):
        print('sensor: ', sensor)
        print('asens: ', self.sensors)
        #nested method
        def _getObstacleDist(sensorHandler_): #from original implementation
            print('working')
            # Get raw sensor readings using API
            rawSR = self.vrep.simxReadProximitySensor(self.client, sensorHandler_, vrepConst.simx_opmode_oneshot_wait)
            #print('rawsr', rawSR)
            # Calculate Euclidean distance
            if rawSR[1]: # if true, obstacle is within detection range, return distance to obstacle
                return math.sqrt(rawSR[2][0]*rawSR[2][0] + rawSR[2][1]*rawSR[2][1] + rawSR[2][2]*rawSR[2][2])
            else: # if false, obstacle out of detection range, return inf.
                return float('inf')

        #invalid sensor key
        if sensor not in self.sensors.values():
            return -1
        return _getObstacleDist(sensor)
