"""
metering.py,

copyright (c) 2015 by Stefan Lehmann,
licensed under the MIT license

"""

import psutil
from collections import namedtuple


ProcessInfo = namedtuple('ProcessInfo', 'id name cpu mem')


def cpu_pct():
    return psutil.cpu_percent()


def mem_pct():
    return psutil.virtual_memory().percent


def list_processes():
    processes = []
    for process in psutil.process_iter():
        try:
            id = process.pid
            name = process.name()
        except psutil.ZombieProcess:
            continue

        try:
            cpu = process.cpu_percent()
            mem = process.memory_percent()
        except (psutil.ZombieProcess, psutil.AccessDenied):
            continue

        processes.append(ProcessInfo(id, name, cpu, mem)._asdict())
    return processes
