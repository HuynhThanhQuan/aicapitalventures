import os

# Set initial setup for project location
PROJECT_LOCATION = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Set initial environment variables
os.environ['AICV'] = PROJECT_LOCATION

# Import necessary packages
import credential


if __name__=='__main__':
    print(os.environ.get('AICV'))
    print(os.environ['AICV_GDRIVE_CRED'])
    print(os.environ['AICV_GDRIVE_TOKEN'])