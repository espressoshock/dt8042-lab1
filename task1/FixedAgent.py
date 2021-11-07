
###########################
### FixedAgent Class
##########################

from Agent import Agent

class FixedAgent(Agent):
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