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
from colorama import Fore, Back, Style, init


class Simulation():
    #########################
    ### SIM-CONSTANTS
    #########################
    TARGET_COLLECTION_RANGE = 0.5
    SIM_STEP_DT_PRECISE = 25
    SIM_STEP_DT_FAST = 100
    TOP_SPEED = 7 * 60 * math.pi / 180  # 7*60deg/s

    #########################
    ### CONSOLE SIMBOLS
    #########################

    # =============
    # == Symbols ==
    # =============

    CONSOLE_SYM_LINK = '🔗'
    CONSOLE_SYM_ANTENNA = '📡'
    CONSOLE_SYM_ID = '🆔'
    CONSOLE_SYM_PLAY = '⏩'
    CONSOLE_SYM_STOP = '⏹️'

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
        init()  # initialize colorama
        print(f'{Fore.YELLOW} {Simulation.CONSOLE_SYM_ANTENNA} Inititializing sim. connection...{Style.RESET_ALL}')
        client = vrep.simxStart(
            connectionAddress=address,
            connectionPort=port,
            waitUntilConnected=True,
            doNotReconnectOnceDisconnected=doNotReconnect,
            timeOutInMs=timeOutInMs,
            commThreadCycleInMs=commThreadCycleinMs)
        if client == vrepConst.simx_return_ok:
            print(
                f'{Fore.GREEN} {Simulation.CONSOLE_SYM_LINK} Connection to remote API established @ {address}:{port}{Style.RESET_ALL}')
            print(
                f'\t{Fore.CYAN}{Simulation.CONSOLE_SYM_ID} Client ID: {client}{Style.RESET_ALL}')
            print(
                f'\t{Fore.BLUE} Connection type: {"Synchronous" if synchronous else "Asynchronous"}{Style.RESET_ALL}')
            #enable synch.conn.mode
            if synchronous:
                syncRes = vrep.simxSynchronous(clientID=client, enable=True)
                vrep.simxStartSimulation(
                    clientID=client, operationMode=vrepConst.simx_opmode_blocking)
                if syncRes != vrepConst.simx_return_ok:  # server error, sync.mode not enabled
                    print(
                        f'{Back.RED} Server error, synchronized mode not enabled, quitting... {Style.RESET_ALL}')
                    quit()
                else:
                    print(
                        f'\t{Fore.GREEN} [Synchronized mode enabled and accepted] {Style.RESET_ALL}')
            else:  # Asynchronous
                vrep.simxStartSimulation(
                    clientID=client, operationMode=vrepConst.simx_opmode_oneshot)
            customDt = Simulation.SIM_STEP_DT_FAST if fast else Simulation.SIM_STEP_DT_PRECISE
            simSetRes = vrep.simxSetFloatingParameter(
                client, vrepConst.sim_floatparam_simulation_time_step, customDt, vrepConst.simx_opmode_oneshot)
            if simSetRes > 0:
                print(
                    f'\t{Fore.GREEN} [Simulation step (dt) set to [{"Fast" if fast else "Precise"} Mode] => {customDt} ] {Style.RESET_ALL}')
            else:
                print(
                    f'{Back.RED} Error when setting custom simulation dt, make sure you have set a custom simulation time step in V-REP!{Style.RESET_ALL}')
            # get objects
            res, objs = vrep.simxGetObjects(
                client, vrepConst.sim_handle_all, vrepConst.simx_opmode_oneshot_wait)
            #successful
            if res == vrepConst.simx_return_ok:
                print(
                    f'\t{Fore.BLUE} [Number of objects in scene {len(objs)}]{Style.RESET_ALL}')
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
                ret_sl,  ultraSonicSensorFrontLeft = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor3', vrepConst.simx_opmode_oneshot_wait)
                ret_sl,  ultraSonicSensorFrontRight = vrep.simxGetObjectHandle(
                    client, 'Pioneer_p3dx_ultrasonicSensor6', vrepConst.simx_opmode_oneshot_wait)
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
                           'frontLeftUltrasonic': ultraSonicSensorFrontLeft,
                           'frontRightUltrasonic': ultraSonicSensorFrontRight,
                           'backUltrasonic': ultraSonicSensorBack,
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

        # set simulation
        self._agent.simulation = self

        ## start auto-collect daemon for target fetching
        #Asynchronous: separate thread approach
        dThread = Thread(
            target=self._collectTargetsDaemon, args=(True,), daemon=True)  # make sure daemon->destroyed after _exit_
        #dThread.start()

        # init agent strategy
        print(f'\n\n{Back.WHITE}{Fore.BLACK} {Simulation.CONSOLE_SYM_PLAY} Simulation in progress...{Style.RESET_ALL}')
        print(f'{Back.CYAN}{Fore.BLACK}  Agent  {Back.YELLOW} {type.capitalize()}  {Style.RESET_ALL}\n')
        self._agent.act()
        print(f'\n\n{Back.WHITE}{Fore.BLACK} {Simulation.CONSOLE_SYM_STOP}  Simulation of a {type.capitalize()} Agent Terminated. {Style.RESET_ALL}\n')

        # print collected targets
        print(f'\n {Back.GREEN}{Fore.BLACK} 📦 Collected {Back.CYAN}  {len(self._agent.targetsCollected)}  {Style.RESET_ALL}')

    #########################
    ### Sim.Helpers
    #########################
    ## Find targets (energy blocks)
    def findTargets(self):
        res = []
        retCode, agentPosition = vrep.simxGetObjectPosition(
            self._client, self._agent._agentHandle, -1, vrepConst.simx_opmode_oneshot_wait)
        for handle, name, position in self._env.targets:
            relativePos = [position[0] - agentPosition[0],
                           position[1] - agentPosition[1]]
            # compute Euclidean distance (in 2-D)
            distance = math.sqrt(relativePos[0]**2 + relativePos[1]**2)
            absDirection = math.atan2(relativePos[0], relativePos[1])
            direction = (position[2] / (2*math.pi))*360
            #direction = self.normalizeAngle(absDirection - self._agent.orientation)
            res.append((handle, name, distance, direction))
        res.sort(key=lambda xx: xx[2])
        return res

    ## collects targets in TARGET_COLLECTION_RANGE
    def collectTargets(self, missLog: bool = True, hitLog: bool = True):
        handle, name, distance, direction = self.findTargets()[0]
        if distance <= self.TARGET_COLLECTION_RANGE + 0.0:
            # hide targets under floor
            vrep.simxPauseCommunication(self._client, 1)
            vrep.simxSetObjectPosition(
                self._client, handle, -1, [1000, 1000, -2], vrepConst.simx_opmode_oneshot)
            vrep.simxPauseCommunication(self._client, 0)
            #update env targets
            self._env.targets[name][-1] = [1000, 1000, -2]
            self._agent.targetCollected(handle)  # targets collected
            if hitLog:
                print(
                    f'\n{Back.GREEN}{Fore.BLACK} ✔ Target collected successfully!  {Back.CYAN} {distance:.1f} unit(s){Style.RESET_ALL}')
            return handle
        if missLog:
            print(
                f'\n❌ No targets within {self.TARGET_COLLECTION_RANGE} unit(s), closest @ {0.0 if math.isnan(distance) else distance:.1f} unit(s)')
        return False

    ## __collectTargets -> Daemon
    def _collectTargetsDaemon(self, log: bool = True):
        while True:
            if log:
                print(self.collectTargets())
            else:
                self.collectTargets()  # threaded iss.here

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
