NAME = 'TCBS'
VERSION = '0.0.1'
LICENSE = 'To be udpated'
DESCRIPTION = 'TCBS modules...'
MAINTAINER = 'Huynh Thanh Quan'

import sys
import os
import importlib

# Resolve namespace of security firm modules


from . import capital
from . import customer
from . import ops


def get_capital_management():
    return capital.CustomerCapital()