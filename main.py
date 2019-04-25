from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_socketio import SocketIO
from config import user_list
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
socketio = SocketIO(app)
PORT = int(os.environ.get("PORT"))

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    session.clear()

    if request.method == 'POST':
        if request.form['username'] in user_list.keys() and request.form['password'] == user_list[request.form['username']]:
                session['logged_in'] = True
                return redirect(url_for('chat'))

        else:
            error = 'Invalid credentials'

    return render_template('login.html', error=error)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('chat.html')

@socketio.on('message_event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    socketio.emit('message_event_response', json, callback=chat)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=PORT)
