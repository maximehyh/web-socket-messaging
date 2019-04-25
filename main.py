from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
socketio = SocketIO(app)


@app.route('/')
def home(methods=['GET', 'POST']):
    return render_template('home.html')

@socketio.on('message_event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    socketio.emit('message_event_response', json, callback=home)


if __name__ == '__main__':
    socketio.run(app, debug=True)
