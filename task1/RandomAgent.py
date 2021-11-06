###########################
### RandomAgent Class
##########################

from Agent import Agent

class RandomAgent(Agent):
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