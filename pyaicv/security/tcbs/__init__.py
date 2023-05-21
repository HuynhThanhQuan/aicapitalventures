NAME = 'TCBS'
VERSION = '0.0.1'
LICENSE = 'To be udpated'
DESCRIPTION = 'TCBS modules...'
MAINTAINER = 'Huynh Thanh Quan'

import sys
import os
import importlib
import logging

from . import api
from .config import SPECIFICATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RequestHandler:
    def __init__(self, message):
        self.message=message

    def __check_apiKey(self):
        # TODO:  check apiKey
        pass

    def __digest(self):
        self.api_handler = api.APIHandler(self.message['api'], self.message['content'])

    def execute(self):
        self.__digest()
        return self.api_handler.execute()


def init(config):
    SPECIFICATION.set(config)


def request(message):
    req_handler = RequestHandler(message)
    response = req_handler.execute()
    return response