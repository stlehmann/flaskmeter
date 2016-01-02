#!/usr/bin/env python

"""
sockettest.py,

copyright (c) 2015 by Stefan Lehmann,
licensed under the MIT license

"""

from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
from forms import DataForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    form = DataForm()
    return render_template('index.html', form=form)

@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)