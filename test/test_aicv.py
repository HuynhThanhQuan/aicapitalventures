import sys
import os

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pyaicv import aicv


def test_set_remote_party():
    aicv.set_remote_party('drive')
    assert aicv.REMOTE is not None

def test_set_remote_party_throw_exception():
    with pytest.raises(aicv.RemoteThirdPartyNotImplementedError):
        aicv.set_remote_party('aws')