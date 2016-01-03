"""
app.py,

copyright (c) 2015 by Stefan Lehmann,
licensed under the MIT license

"""
import json
import plotly
from enum import Enum


class Pages(Enum):
    cpu = 1
    processes = 2


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

# refresh time in seconds
REFRESH_TIME = 1
BUFFER_SIZE = 120

# currently active page
current_page = Pages.cpu

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()


import time
import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread
from .forms import DataForm
from . import meter


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


cpu_data = dict(x=[], y=[], type='scatter', name='cpu %')
mem_data = dict(x=[], y=[], type='scatter', name='mem %')


graphs = [
    dict(
        data=[cpu_data, mem_data],
        layout=dict()
    )
]


def background_thread():

    global cpu_data
    global mem_data
    global current_page

    while True:
        time.sleep(REFRESH_TIME)
        # get current data
        cur_time = str(datetime.datetime.now())
        cur_cpu = meter.cpu_pct()
        cur_mem = meter.mem_pct()

        # remove old data
        if len(cpu_data['x']) >= BUFFER_SIZE:
            cpu_data['x'].pop(0)
            cpu_data['y'].pop(0)
            mem_data['x'].pop(0)
            mem_data['y'].pop(0)

        # save cpu data
        cpu_data['x'].append(cur_time)
        cpu_data['y'].append(cur_cpu)

        # save mem data
        mem_data['x'].append(cur_time)
        mem_data['y'].append(cur_mem)

        if current_page == Pages.cpu:

            socketio.emit(
                'cpu_mem',
                {
                    'time': cur_time,
                    'cpu': cur_cpu,
                    'mem': cur_mem
                },
                namespace='/test'
            )
        elif current_page == Pages.processes:
            processes = sorted(
                meter.list_processes(), key=lambda x: x['cpu'], reverse=True
            )
            socketio.emit(
                'processlist',
                dict(
                    processes=processes
                ),
                namespace='/test'
            )


@app.route('/')
def index():
    global current_page
    global thread
    current_page = Pages.cpu
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
    graph_json = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', ids=ids, graphJSON=graph_json)

    # return render_template('index.html')


@app.route('/processes')
def handle_processes():
    global current_page
    global thread
    current_page = Pages.processes
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()

    processes = sorted(
        meter.list_processes(), key=lambda x: x['cpu'], reverse=True
    )

    return render_template('processes.html', processes=processes)


if __name__ == '__main__':
    socketio.run(app)
