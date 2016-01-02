"""
app.py,

copyright (c) 2015 by Stefan Lehmann,
licensed under the MIT license

"""
import json
import plotly

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None


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
count = 0


graphs = [
    dict(
        data=[
            dict(
                x=[],
                y=[],
                type='scatter',
                name='cpu %'
            ),
            dict(
                x=[],
                y=[],
                type='scatter',
                name='mem %'
            )
        ],
        layout=dict(
        )
    )
]


def background_thread():
    global count
    while True:
        count += 1
        time.sleep(1)
        socketio.emit(
            'my response',
            {
                'count': count,
                'time': str(datetime.datetime.now()),
                'cpu': meter.cpu_pct(),
                'mem': meter.mem_pct()
            },
            namespace='/test'
        )


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
    graph_json = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', ids=ids, graphJSON=graph_json)

    # return render_template('index.html')


@socketio.on('clicked', namespace='/test')
def handle_clicked(data):
    socketio.emit('clicked_back', {'clicked': data['data']}, namespace='/test')


if __name__ == '__main__':
    socketio.run(app)
