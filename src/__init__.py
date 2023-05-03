import os

# Set initial setup for project location
PROJECT_LOCATION = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Set initial environment variables
os.environ['AICV'] = PROJECT_LOCATION


if __name__=='__main__':
    print(os.environ.get('AICV'))