NAME = 'TCBS'
VERSION = '0.0.1'
LICENSE = 'To be udpated'
DESCRIPTION = 'TCBS modules...'
MAINTAINER = 'Huynh Thanh Quan'

import sys
import os
import importlib
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.info(f"{NAME} module is set")


from . import ops


def get_all_customer_info():
    return ops.get_all_customer_info()


def get_customer_info(name):
    return ops.get_customer_info(name)