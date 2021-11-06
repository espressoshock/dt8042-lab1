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
    def __init__(self, name: str, actuators: dict, sensors: dict, client: str):
        self._client = client
        self._actuators = actuators
        self._sensors = sensors

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

    ## Angle normalization
    def _normalizeAngle(self, angle: float):
        while angle > math.pi:
            angle -= 2*math.pi
        while angle < -math.pi:
            angle += 2*math.pi
        return angle
