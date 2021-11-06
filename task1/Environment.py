###########################
### Environment Class
##########################

# =IMPORTS
from libs import vrep
from libs import vrepConst
import math
import time
import random


class Environment():
    #########################
    ### Constructor
    #########################
    def __init__(self, targets: list):
        self._targets = targets

    #########################
    ### PROPS
    #########################
    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, value):
        self._targets = value
