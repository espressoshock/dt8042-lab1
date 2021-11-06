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
            vrep.simxPauseCommunication(self._client, 0) #resume


    
