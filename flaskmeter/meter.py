"""
metering.py,

copyright (c) 2015 by Stefan Lehmann,
licensed under the MIT license

"""

import psutil


def cpu_pct():
    return psutil.cpu_percent()


def mem_pct():
    return psutil.virtual_memory().percent
