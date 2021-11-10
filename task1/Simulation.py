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
from threading import Thread


class Simulation():
    #########################
    ### SIM-CONSTANTS
    #########################
    TARGET_COLLECTION_RANGE = 0.5
    SIM_STEP_DT_PRECISE = 25
    SIM_STEP_DT_FAST = 100
    TOP_SPEED = 7 * 60 * math.pi / 180  # 7*60deg/s

    #########################
    ### Constructor
    #########################
    def __init__(self, agent: Agent, environment: Environment, connectionTime: str, client, synchronous: bool = True):
        self._agent = agent
        self._env = environment
        self._connectionTime = connectionTime
        self._client = client
        self._synchronous = synchronous

    #########################
    ### VREP-init
    #########################
    @classmethod
    def init(cls, address='127.0.0.1', port=19999, doNotReconnect=True, timeOutInMs=5000, commThreadCycleinMs=5, synchronous: bool = True, fast: bool = True):
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
            print(
                f'Connection type: {"Synchronous" if synchronous else "Asynchronous"}')
            #enable synch.conn.mode
            if synchronous:
                syncRes = vrep.simxSynchronous(clientID=client, enable=True)
                vrep.simxStartSimulation(
                    clientID=client, operationMode=vrepConst.simx_opmode_blocking)
                if syncRes != vrepConst.simx_return_ok:  # server error, sync.mode not enabled
                    print(f'Server error, synchronized mode not enabled, quitting...')
                    quit()
                else:
                    print(f'[Synchronized mode enabled and accepted]')
            else:  # Asynchronous
                vrep.simxStartSimulation(
                    clientID=client, operationMode=vrepConst.simx_opmode_oneshot)
            customDt = Simulation.SIM_STEP_DT_FAST if fast else Simulation.SIM_STEP_DT_PRECISE
            simSetRes = vrep.simxSetFloatingParameter(
                client, vrepConst.sim_floatparam_simulation_time_step, customDt, vrepConst.simx_opmode_oneshot)
            if simSetRes == vrepConst.simx_return_ok:
                print(
                    f'[Simulation step (dt) set to [{"Fast" if fast else "Precise"} Mode] => {customDt} ]')
            else:
                print(
                    f'Error when setting custom simulation dt, make sure you have set a custom simulation time step in V-REP!')
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
                res, simulationDt = vrep.simxGetFloatingParameter(
                    client, vrepConst.sim_floatparam_simulation_time_step,
                    vrepConst.simx_opmode_blocking)
                actuators = {'leftMotor': leftMotorHandle,
                             'rightMotor': rightMotorHandle}
                sensors = {'leftFrontUltrasonic': ultraSonicSensorLeftFront,
                           'leftBackUltrasonic': ultraSonicSensorLeftBack,
                           'frontUltrasonic': ultraSonicSensorFront,
                           'rightFrontUltrasonic': ultraSonicSensorRightFront,
                           'rightBackUltrasonic': ultraSonicSensorRightBack,
                           'targetSensor': pioneerRobotHandle}
                return cls(Agent(None, actuators, sensors, pioneerRobotHandle, client, simulationDt, Simulation.TOP_SPEED, synchronous), Environment(blockHandleArray), connectionTime, client)
            else:  # API error
                print(f'Error: Remote API error [{res}]')
                quit()
        else:  # client => -1
            print(f'Error: Connection failed')
            quit()

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

        ## start auto-collect daemon for target fetching
        dThread = Thread(
            target=self._collectTargetsDaemon, args=(False,), daemon=True)  # make sure daemon->destroyed after _exit_
        dThread.start()

        # init agent strategy
        print(f'Simulation of a {type.capitalize()} Agent in progress...')
        self._agent.act()
        print(f'Simulation of a {type.capitalize()} Agent Terminated.')

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

    ## __collectTargets -> Daemon
    def _collectTargetsDaemon(self, log: bool = False):
        while True:
            if log:
                print(self._collectTargets())
            else:
                self._collectTargets()

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
        #stop simulation
        vrep.simxStopSimulation(self._client, vrepConst.simx_opmode_blocking)
        #close connection
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

    @property
    def simulationStep(self):
        res, dt = vrep.simxGetFloatingParameter(
            self._client, vrepConst.sim_floatparam_simulation_time_step,
            vrepConst.simx_opmode_blocking)
        return dt if res == vrepConst.simx_return_ok else res
