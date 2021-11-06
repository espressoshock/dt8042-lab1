###########################
### Environment Class
##########################

# =IMPORTS
from libs import vrep
from libs import vrepConst
import math, time, random

class Environment():
    #########################
    ### Constructor
    #########################
    def __init__(self, blocks: list):
        self._blocks = blocks

    #########################
    ### PROPS
    #########################
    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, value):
        self._blocks = value