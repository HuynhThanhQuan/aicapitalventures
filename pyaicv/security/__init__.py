import os
import sys
import importlib
import logging
import yaml


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SecurityFirmNotSelected(Exception):
    pass


class SecurityFirmFactory(dict):
    def __init__(self):
        self.warmup()

    def warmup(self):
        security_cfg = yaml.safe_load(os.environ['AICV_SECURITY'])
        self.aicv_security = {sec_spec['name']: sec_spec for sec_spec in security_cfg}

    def __find_security_module(self, name):
        lower_name = name.lower()
        sec_module = os.path.dirname(__file__)
        sel_sec_module = os.path.join(sec_module, lower_name)
        if os.path.exists(sel_sec_module):
            sys.path.append(sec_module)
            return True
        return False

    def get(self, name):
        name = name.lower()
        if name not in self.__dict__.keys():
            if self.__find_security_module(name):
                self.__dict__[name] = importlib.import_module(name.lower())
                self.__dict__[name].init(self.aicv_security[name])
            else:
                raise ModuleNotFoundError(f"Security Firm {name} not implemented")
        return self.__dict__[name]


FACTORY = SecurityFirmFactory()