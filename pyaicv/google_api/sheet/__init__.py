import logging

from google_api import credential
from google_api.sheet.exception import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def update_values(spreadsheet_id, range_name, value_input_option, values):
    try:
        service = build('sheets', 'v4', credentials=creds)
        values = [
            [
                # Cell values ...
            ],
            # Additional rows ...
        ]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        logger.debug(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        logger.exception(f"An error occurred: {error}")
        return error