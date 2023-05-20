import os
import sys
import importlib
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SecurityFirmNotSelected(Exception):
    pass


class SecurityFirmFactory(dict):
    def __init__(self):
        self.active_security = None

    def __find_security_module(self, name):
        lower_name = name.lower()
        sec_module = os.path.dirname(__file__)
        sel_sec_module = os.path.join(sec_module, lower_name)
        if os.path.exists(sel_sec_module):
            sys.path.append(sec_module)
            return True
        return False

    def set(self, name):
        if self.__find_security_module(name):
            self.__dict__[name] = importlib.import_module(name.lower())
            self.active_security = self.__dict__[name]
        else:
            raise ModuleNotFoundError(f"Security Firm {name} not implemented")

    def get(self, name):
        return self.__dict__[name]

    def get_active_security(self):
        if self.active_security is None:
            raise SecurityFirmNotSelected("Please set Security Firm first")
        return self.active_security


factory = SecurityFirmFactory()