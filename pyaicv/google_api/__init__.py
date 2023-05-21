import os
import sys
import importlib
import logging
import pathlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


__EXCLUDED__ = [
    '__pycache__',
    '.ipynb_checkpoints'
]


class ServiceNotImplementedError(Exception):
    pass


class GoogleServiceManagement:
    def __init__(self):
        self.find_google_services()

    def find_google_services(self):
        self.service = {}
        google_module = os.path.dirname(__file__)

        service_modules = []
        for f in os.listdir(google_module):
            if os.path.isdir(os.path.join(google_module, f)):
                fp = pathlib.Path(os.path.join(google_module, f))
                if fp.name not in __EXCLUDED__:
                    iter_files = list(fp.iterdir())
                    if '__init__.py' in [i.name for i in iter_files]:
                        service_modules.append(f)

        sys.path.append(google_module)
        for s in service_modules:
            logger.debug(f'\tImporting google service: {s} ')
            self.service[s] = importlib.import_module(s)

    def get_service(self, service_name):
        if service_name not in self.service.keys():
            raise ServiceNotImplementedError(f'Service {service_name} not found')
        return self.service[service_name]


def service(service_name):
    return service_management.get_service(service_name)


service_management = GoogleServiceManagement()
