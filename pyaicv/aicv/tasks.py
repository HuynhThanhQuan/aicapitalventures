import logging

import security

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def upload_TCBS_reviewed_data():
    # TODO: header
    message = {
        # TODO: API key, session
        'apiKey': None,
        'session': None,
        'api': 'upload',
        'content': {}
    }
    response = security.FACTORY.get('TCBS').request(message)
    logger.debug(f'Response body \n {response}')


def get_TCBS_summary_report():
    # TODO: header
    message = {
        # TODO: API key, session
        'apiKey': None,
        'session': None,
        'api': 'report',
        'content': {
            'type': 'summary',
            'customers': ['*'],
            'fields': ['totalAsset'],
            'operations': ['diff', 'pct'],
            'output':{
                'storage': 'local',
                'format': 'xlsx'
            }
        }
    }
    response =  security.FACTORY.get('TCBS').request(message)
    logger.debug(f'Response body \n {response}')


def get_TCBS_customer_report(customer_name):
    # TODO: header
    message = {
        # TODO: API key, session
        'apiKey': None,
        'session': None,
        'api': 'report',
        'content': {
            'type': 'summary',
            'customers': [customer_name],
            'fields': ['totalAsset'],
            'operations': ['diff', 'pct']
        }
    }
    response =  security.FACTORY.get('TCBS').request(message)
    logger.debug(f'Response body \n {response}')
