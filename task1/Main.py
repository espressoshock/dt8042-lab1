###########################
### Task 1 : Main entry Point
##########################

## =IMPORTS
from Environment import Environment
from Agent import Agent

import time

def main():
    env = Environment('127.0.0.1', 19999)
    clientID = env.init()
    objs = env.getObjects(clientID)
    agent = Agent(objs['client'], objs['vrep'], objs['actuators'], objs['sensors'])
    start = env.simulationTime
    while True:
        print('Comp: ', start, env.simulationTime)
        if env.simulationTime >= start + 1000:
            break
        agent._setMotorSpeed('left', 1)
    print('-------->while over')
    agent._setMotorSpeed('left', 0)

    '''
    start = time.time()
    while time.time() < start + 5:
       # stime = env.connectiontime
       # print('stime: ', stime)
        agent._setMotorSpeed('left', 1)
        agent._setMotorSpeed('right', 1.5)
    agent._setMotorSpeed('left', 0)
    agent._setMotorSpeed('right', 0)
    '''

    env.close()
    #print('list: ', objs['sensors'])
    #print('value: ', agent.getSensorReading(objs['sensors']['leftUltrasonic']))
    


if __name__ == '__main__':
    main()