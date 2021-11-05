###########################
### Environment Class
##########################

# =IMPORTS
from libs import vrep
from libs import vrepConst
import math, time, random

class Environment():
    #nested dict
    #legacy: to conform with provided code (back-compatible)
    class DictMapping(dict):
        def __init__(self, *args, **kwargs):
            super(self.inner.DictMapping, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def __init__(self, addr='127.0.0.1', port=19999):
        self.addr=addr
        self.port = port
        self.connectionTime = 0
        self.client = None
    #init connection
    # returns client
    def init(self):
        print('Inititializing sim. connection...')
        #vrep.simxFinish(-1) # just in case, close all opened connections
        # simxStart(string connectionAddress,number connectionPort,boolean 
        # waitUntilConnected,boolean doNotReconnectOnceDisconnected,number timeOutInMs,
        # number commThreadCycleInMs)
        self.client =  vrep.simxStart(self.addr, self.port, True, True, 5000, 5) # connect to server
        print(f'Client ID: {self.client}')
        return self.client
    # retrieve objects 
    def getObjects(self, client):
        if client != -1:
            print(f'Connection to remote API established @ {self.addr}:{self.port}')
            # get objects
            res, objs = vrep.simxGetObjects(client,vrepConst.sim_handle_all,vrepConst.simx_opmode_oneshot_wait)
            #successful
            if res == vrepConst.simx_return_ok:
                print(f'[Number of objects in scene {len(objs)}')
                ret_lm,  leftMotorHandle = vrep.simxGetObjectHandle(client, 'Pioneer_p3dx_leftMotor', vrepConst.simx_opmode_oneshot_wait)
                ret_rm,  rightMotorHandle = vrep.simxGetObjectHandle(client, 'Pioneer_p3dx_rightMotor', vrepConst.simx_opmode_oneshot_wait)
                ret_pr,  pioneerRobotHandle = vrep.simxGetObjectHandle(client, 'Pioneer_p3dx', vrepConst.simx_opmode_oneshot_wait)
                ret_sl,  ultraSonicSensorLeft = vrep.simxGetObjectHandle(client, 'Pioneer_p3dx_ultrasonicSensor3',vrepConst.simx_opmode_oneshot_wait)
                ret_sr,  ultraSonicSensorRight = vrep.simxGetObjectHandle(client, 'Pioneer_p3dx_ultrasonicSensor5',vrepConst.simx_opmode_oneshot_wait)
                blockHandleArray = []
                for i_block in range(12):
                    blockName = 'ConcretBlock#'+str(i_block)
                    retCode, handle = vrep.simxGetObjectHandle(client, blockName, vrepConst.simx_opmode_oneshot_wait)
                    assert retCode==0, retCode
                    if i_block>6:
                        rand_loc = [random.random()*6-1.5, random.random()*7-2.5, 0.0537] # x[-1.5,4.5] y[-2.5,-4.5]
                        vrep.simxSetObjectPosition(client, handle, -1, rand_loc, vrepConst.simx_opmode_oneshot_wait)
                    retCode,position = vrep.simxGetObjectPosition(client, handle, -1, vrepConst.simx_opmode_oneshot_wait)
                    assert retCode==0, retCode
                    blockHandleArray.append([handle,i_block,position])
                self.connectionTime = vrep.simxGetLastCmdTime(client)
                actuators = [leftMotorHandle, rightMotorHandle, pioneerRobotHandle]
                sensors = [ultraSonicSensorLeft, ultraSonicSensorRight, None]
                return {'actuators': actuators, 'sensors': sensors, 'client': client, 'vrep': vrep}
                '''
                return self.inner.DictMapping(clientID=client,
                             leftMotorHandle=leftMotorHandle,
                             rightMotorHandle=rightMotorHandle,
                             pioneerRobotHandle=pioneerRobotHandle,
                             ultraSonicSensorLeft=ultraSonicSensorLeft,
                             ultraSonicSensorRight=ultraSonicSensorRight,
                             energySensor=None)
                '''
            else: # API error
                print(f'Error: Remote API error [{res}]')
                return -1
            vrep.simxFinish(client)
        else: # client => -1
            print(f'Error: Connection failed')
        return -1

