import os

import pandas as pd

from pyaicv.security import factory as sec_factory

from . import analyser as als


def set_security_firm(security):
    sec_factory.set(security)


def run_analysis():
    als.set_security_analyser(sec_factory.get_active_security())
    als.run_full_analysis()
    

def export_report():
    als.export_summary_report()
