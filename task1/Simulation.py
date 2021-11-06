###########################
### Simulation Class
##########################
from FixedAgent import FixedAgent
from MemoryAgent import MemoryAgent
from RandomAgent import RandomAgent
from ReflexAgent import ReflexAgent
from libs import vrep
from libs import vrepConst
from Agent import Agent
from Environment import Environment
import math
import random


class Simulation():
    #########################
    ### SIM-CONSTANTS
    #########################
    TARGET_COLLECTION_RANGE = 0.5

    #########################
    ### Constructor
    #########################
    def __init__(self, agent: Agent, environment: Environment, connectionTime: str, client):
        self._agent = agent
        self._env = environment
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
                #########################
                ### Motors
                #########################
                ret_lm,  leftMotorHandle = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_leftMotor', vrepConst.simx_opmode_oneshot_wait)
                ret_rm,  rightMotorHandle = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_rightMotor', vrepConst.simx_opmode_oneshot_wait)
                #########################
                ### Robot (used as target finder [ref])
                #########################
                ret_pr,  pioneerRobotHandle = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx', vrepConst.simx_opmode_oneshot_wait)
                #########################
                ### Sensors
                #########################
                ####### Left ############
                ret_sl,  ultraSonicSensorLeftFront = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor1', vrepConst.simx_opmode_oneshot_wait)
                ret_sl,  ultraSonicSensorLeftBack = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor16', vrepConst.simx_opmode_oneshot_wait)
                ####### Front ############
                ret_sl,  ultraSonicSensorFront = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor4', vrepConst.simx_opmode_oneshot_wait)
                ####### Right ############
                ret_sl,  ultraSonicSensorRightFront = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor8', vrepConst.simx_opmode_oneshot_wait)
                ret_sl,  ultraSonicSensorRightBack = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor9', vrepConst.simx_opmode_oneshot_wait)
                ####### Back ############
                ret_sl,  ultraSonicSensorBack = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor13', vrepConst.simx_opmode_oneshot_wait)
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
                             'rightMotor': rightMotorHandle}
                sensors = {'leftFrontUltrasonic': ultraSonicSensorLeftFront,
                           'leftBackUltrasonic': ultraSonicSensorLeftBack,
                           'frontUltrasonic': ultraSonicSensorFront,
                           'rightFrontUltrasonic': ultraSonicSensorRightFront,
                           'rightBackUltrasonic': ultraSonicSensorRightBack,
                           'targetSensor': pioneerRobotHandle}
                return cls(Agent(None, actuators, sensors, pioneerRobotHandle, client), Environment(blockHandleArray), connectionTime, client)
            else:  # API error
                print(f'Error: Remote API error [{res}]')
                return -1
        else:  # client => -1
            print(f'Error: Connection failed')
        return -1

    #########################
    ### Sim.Starters
    #########################
    ## Starter entry point
    def start(self, type: str = 'random'):
        # casting to specialization
        if type == 'random':
           self._agent.__class__ = RandomAgent
        elif type == 'fixed':
            self._agent.__class__ = FixedAgent
        elif type == 'reflex':
            self._agent.__class__ = ReflexAgent
        else:  # agent with memory => 'memory'
            self._agent.__class__ = MemoryAgent
        # init agent strategy
        self._agent.act()

    #########################
    ### Sim.Helpers
    #########################
    ## Find targets (energy blocks)
    def _findTargets(self):
        res = []
        retCode, agentPosition = vrep.simxGetObjectPosition(
            self._client, self._agent._agentHandle, -1, vrepConst.simx_opmode_oneshot_wait)
        for handle, name, position in self._env.targets:
            relativePos = [position[0] - agentPosition[0],
                           position[1] - agentPosition[1]]
            # compute Euclidean distance (in 2-D)
            distance = math.sqrt(relativePos[0]**2 + relativePos[1]**2)
            absDirection = math.atan2(relativePos[0], relativePos[1])
            direction = Simulation.normalizeAngle(
                absDirection - self._agent.orientation)
            res.append((handle, name, distance, direction))
        res.sort(key=lambda xx: xx[2])
        return res

    ## collects targets in TARGET_COLLECTION_RANGE
    def _collectTargets(self):
        handle, name, distance, direction = self._findTargets()[0]
        if distance <= self.TARGET_COLLECTION_RANGE:
            # hide targets under floor
            vrep.simxPauseCommunication(self._client, 1)
            vrep.simxSetObjectPosition(
                self._client, handle, -1, [1000, 1000, -2], vrepConst.simx_opmode_oneshot)
            vrep.simxPauseCommunication(self._client, 0)
            #update env targets
            self._env.targets[name][-1] = [1000, 1000, -2]
            return (f'Target collected successfully!')
        return (f'No targets within {self.TARGET_COLLECTION_RANGE} unit(s)')

    #########################
    ### Class methods
    #########################
    ## Angle normalization
    @classmethod
    def normalizeAngle(cls, angle: float):
        while angle > math.pi:
            angle -= 2*math.pi
        while angle < -math.pi:
            angle += 2*math.pi
        return angle

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
    def environment(self):
        return self._env

    @property
    def simulationTime(self):
        vrep.simxGetPingTime(self._client)
        return vrep.simxGetLastCmdTime(self._client)
