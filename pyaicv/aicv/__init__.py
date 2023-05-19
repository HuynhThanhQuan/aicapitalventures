from .exception import *



class RemoteThirdPartyInterface(dict):
    def __init__(self):
        pass


class DriveRemoteThirdParty(RemoteThirdPartyInterface):
    def __init__(self):
        pass



REMOTE = None


def set_remote_party(third_party):
    global REMOTE
    if third_party.lower() == 'drive':
        REMOTE = DriveRemoteClass()
    else:
        raise RemoteThirdPartyNotImplementedError(f'{third_party} remote is not implemented')

