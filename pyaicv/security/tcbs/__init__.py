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


def get_all_customer_info():
    return ops.get_all_customer_info()


def get_customer_info(name):
    return ops.get_customer_info(name)