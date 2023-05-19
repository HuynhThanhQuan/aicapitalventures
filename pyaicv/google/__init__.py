import os
import sys
import importlib

class GoogleServiceManagement:
    def __init__(self):
        self.find_google_services()

    def find_google_services(self):
        self.service = {}
        google_module = os.path.dirname(__file__)
        service_modules = os.listdir(google_module)
        sys.path.append(google_module)
        for s in service_modules:
            self.service[s] = importlib.import_module(s)

    def get_service(self, service_name):
        if service_name not in self.service.keys():
            raise ServiceNotImplementedError(f'Service {service_name} not found')
        return self.service[service_name]


def service(service_name):
    return service_management.get_service(service_name)


service_management = GoogleServiceManagement()
