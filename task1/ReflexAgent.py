###########################
### ReflexAgent Class
##########################

from Agent import Agent

class ReflexAgent(Agent):
    #########################
    ### Constructor
    #########################
    def __init__(self):
        super().__init__()

    #########################
    ### Override
    #########################
    def act(self):
       print('act from child')