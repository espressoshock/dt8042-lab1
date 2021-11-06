###########################
### Simulation Class
##########################
from libs import vrep
from libs import vrepConst
from Agent import Agent
import math
import random


class Simulation():
    #########################
    ### Constructor
    #########################
    def __init__(self, agent: Agent, connectionTime: str, client):
        self._agent = agent
        self._connectionTime = connectionTime
        self._client = client
        self._opMode = vrepConst.simx_opmode_oneshot_wait  # async

    #########################
    ### VREP-init
    #########################
    @classmethod
    def init(cls, address='127.0.0.1', port=19999, doNotReconnect=True, timeOutInMs=5000, commThreadCycleinMs=5):
        vrep.simxFinish(-1)  # just in case, close all opened connections
        print('Inititializing sim. connection...')
        client = vrep.simxStart(
            connectionAddress=address,
            connectionPort=port,
            waitUntilConnected=True,
            doNotReconnectOnceDisconnected=doNotReconnect,
            timeOutInMs=timeOutInMs,
            commThreadCycleInMs=commThreadCycleinMs)
        if client == vrepConst.simx_return_ok:
            print(f'Connection to remote API established @ {address}:{port}')
            print(f'Client ID: {client}')
            # get objects
            res, objs = vrep.simxGetObjects(
                client, vrepConst.sim_handle_all, vrepConst.simx_opmode_oneshot_wait)
            #successful
            if res == vrepConst.simx_return_ok:
                print(f'[Number of objects in scene {len(objs)}')
                ret_lm,  leftMotorHandle = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_leftMotor', vrepConst.simx_opmode_oneshot_wait)
                ret_rm,  rightMotorHandle = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_rightMotor', vrepConst.simx_opmode_oneshot_wait)
                ret_pr,  pioneerRobotHandle = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx', vrepConst.simx_opmode_oneshot_wait)
                ret_sl,  ultraSonicSensorLeft = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor3', vrepConst.simx_opmode_oneshot_wait)
                ret_sr,  ultraSonicSensorRight = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor5', vrepConst.simx_opmode_oneshot_wait)
                blockHandleArray = []
                for i_block in range(12):
                    blockName = 'ConcretBlock#'+str(i_block)
                    retCode, handle = vrep.simxGetObjectHandle(
                        client, blockName, vrepConst.simx_opmode_oneshot_wait)
                    assert retCode == 0, retCode
                    if i_block > 6:
                        # x[-1.5,4.5] y[-2.5,-4.5]
                        rand_loc = [random.random()*6-1.5,
                                    random.random()*7-2.5, 0.0537]
                        vrep.simxSetObjectPosition(
                            client, handle, -1, rand_loc, vrepConst.simx_opmode_oneshot_wait)
                    retCode, position = vrep.simxGetObjectPosition(
                        client, handle, -1, vrepConst.simx_opmode_oneshot_wait)
                    assert retCode == 0, retCode
                    blockHandleArray.append([handle, i_block, position])
                connectionTime = vrep.simxGetLastCmdTime(client)
                actuators = {'leftMotor': leftMotorHandle,
                             'rightMotor': rightMotorHandle, 'pioneerRobot': pioneerRobotHandle}
                sensors = {'leftUltrasonic': ultraSonicSensorLeft,
                           'rightUltrasonic': ultraSonicSensorRight}
                return cls(Agent(None, actuators, sensors, client), connectionTime, client)
            else:  # API error
                print(f'Error: Remote API error [{res}]')
                return -1
        else:  # client => -1
            print(f'Error: Connection failed')
        return -1

    # VREP disconnect
    def disconnect(self):
        # make sure last cmd is sent out
        vrep.simxGetPingTime(self._client)
        vrep.simxFinish(self._client)

    # (with) operator overload
    def __enter__(self):
        return self

    # auto-closing (with)
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    #########################
    ### PROPS
    #########################
    @property
    def agent(self):
        return self._agent

    @property
    def simulationTime(self):
        vrep.simxGetPingTime(self._client)
        return vrep.simxGetLastCmdTime(self._client)