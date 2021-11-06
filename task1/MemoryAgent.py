###########################
### MemoryAgent Class
##########################

from Agent import Agent

class MemoryAgent(Agent):
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