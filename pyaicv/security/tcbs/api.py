import logging

from . import ops


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_customer_info(name):
    return ops.get_customer_info(name)


class APIHandler:
    def __init__(self, api, content):
        self.api = api
        self.content = content
        self.tcbs_ops = ops.TCBS_OPS

    def __handle(self):
        response = None
        if self.api == 'report':
            if self.content['type'] == 'summary':
                customers = self.content['customers']
                report_all_customer = False
                for c in customers:
                    if c == '*':
                        report_all_customer=True
                if report_all_customer:
                    response = self.tcbs_ops.get_all_customer_info()
                else:
                    response = []
                    for c in customers:
                        response.append(self.tcbs_ops.get_customer_info(name))
        elif self.api == 'upload':
            response = self.tcbs_ops.upload_reviewed_data()
        return response

    def execute(self):
        return self.__handle()