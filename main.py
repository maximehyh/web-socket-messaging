from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_socketio import SocketIO, emit, disconnect
from config import user_list
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///message.db'

db = SQLAlchemy(app)
socketio = SocketIO(app)
PORT = int(os.environ.get("PORT"))

logged_users = {}


class Message(db.Model):
    ''' Database including history of messages '''

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route('/', methods=['GET', 'POST'])
def login():
    ''' User login using users specified in config file
    (could be stored within a DB for more safety) '''

    error = None
    db.create_all()

    if request.method == 'POST':
        if (request.form['username'] in user_list.keys() and
           request.form['password'] == user_list[request.form['username']]):
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

    messages = Message.query.all()

    return render_template('chat.html', messages=messages,
                           username=session['username'], user_list=user_list)


@socketio.on('message_event')
def handle_message(json):
    ''' Emit message to all clients and save message in history db '''

    message = Message(message=json['message'])
    db.session.add(message)
    db.session.commit()

    socketio.emit('message_event_response', json, callback=chat)


@socketio.on('username')
def handle_username():
    ''' In order to link logged user to session ID allowing to send
    private messages '''

    logged_users[session['username']] = request.sid


@socketio.on('private_message', namespace='/private')
def private_message(data):
    ''' Emit message to specific user using private socket '''

    session_id = logged_users[data['username']]
    message = data['origin'] + ' : ' + data['message']

    socketio.emit('new_private_message', message, room=session_id)


@socketio.on('disconnect_request')
def disconnect_request():
    session.pop('logged_in', None)
    disconnect()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=PORT)
    # socketio.run(app, debug=True)
