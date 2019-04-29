from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, disconnect
from make_celery import make_celery
from datetime import datetime
import os
import eventlet


# Setting up the flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gv~PUa#<WF[wEI_'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CELERY_BROKER_URL is the URL where the message broker (Redis) is running
# CELERY_RESULT_BACKEND is required to keep track of task and store the status
app.config.update(
    CELERY_BROKER_URL='redis://redis:6379/0',
    CELERY_RESULT_BACKEND='redis://redis:6379/0'
)


# the app is passed to make_celery function, this function sets up celery in 
# order to integrate with the flask application
celery = make_celery(app)

# Message queue can be disabled in order to allow testing
# "Test client cannot be used with a message queue. Disable the queue
# on your test configuration."
# TO DO : MAKE MESSAGE QUEUE WORK WITH DOCKER-COMPOSE
testing = os.environ.get("TESTING")

if testing:
    socketio = SocketIO(app)

else:
    # Instanciating SocketIO for our Flask application
    # with redis as message broker
    socketio = SocketIO(app, message_queue='redis://redis:6379/0', async_mode=os.environ.get("ASYNC_MODE"), logger=True, engineio_logger=True)

    # Cf https://flask-socketio.readthedocs.io/en/latest/
    # "Flask-SocketIO does not apply monkey patching when eventlet or
    # gevent are used. But when working with a message queue, it is very
    # likely that the Python package that talks to the message queue
    # service will hang if the Python standard library is not monkey patched."
    if os.environ.get("ASYNC_MODE") == 'eventlet':
        eventlet.monkey_patch()

# Creating DB
db = SQLAlchemy(app)
db.init_app(app)

logged_users = {}


##########################################
############# DB MODELS ##################
##########################################
class Message(db.Model):
    ''' Model including history of messages '''
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class User(db.Model):
    ''' Model including users '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(300), nullable=False)
    password = db.Column(db.String(300), nullable=False)

##########################################
############# FLASK ROUTES ###############
##########################################
@app.route('/', methods=['GET', 'POST'])
def login():
    ''' User login using users specified in DB'''
    error = None

    registered_users = {}
    for user in User.query.all():
        registered_users[user.username] = user.password

    session['user_list'] = registered_users

    if request.method == 'POST':
        if (request.form['username'] in registered_users.keys() and
           request.form['password'] == registered_users[request.form['username']]):
            session['logged_in'] = True
            session['username'] = request.form['username']

            return redirect(url_for('chat'))
        else:
            error = 'Invalid credentials'

    return render_template('login.html', error=error)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    ''' Chat room for all users. Need to be logged in to acces chat room'''
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_list = session['user_list']

    messages = Message.query.all()

    return render_template('chat.html', messages=messages,
                           username=session['username'], user_list=user_list)


##########################################
############# SOCKET.IO EVENTS ###########
##########################################
@socketio.on('message_event')
def handle_message(json, messaging=False):
    ''' Emit message to all clients and save message in history db '''

    # Saving message in DB
    message = Message(message=json['message'])
    db.session.add(message)
    db.session.commit()

    if testing:
        socketio.emit('message_event_response', json)

    else:
        # Sending task to Celery worker
        message_broadcast.delay(json)


@socketio.on('private_message', namespace='/private')
def private_message(data):
    ''' Emit message to specific user using private socket '''
    session_id = logged_users[data['username']]
    message = data['origin'] + ' : ' + data['message']

    if testing:
        socketio.emit('new_private_message', message, room=session_id)

    else:
        # Sending task to Celery worker
        message_directed.delay(message, session_id)


@socketio.on('username')
def handle_username():
    ''' In order to link logged user to session ID allowing to send
    private messages '''
    logged_users[session['username']] = request.sid


@socketio.on('disconnect_request')
def disconnect_request():
    session.pop('logged_in', None)
    disconnect()


@celery.task(name="task.message_directed")
def message_directed(message, session_id):
    socketio.emit('new_private_message', message, room=session_id)


@celery.task(name="task.message_broadcast")
def message_broadcast(json):
    socketio.emit('message_event_response', json)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='3000')

    # Used when debugging in virtualenv
    # socketio.run(app, debug=True)
