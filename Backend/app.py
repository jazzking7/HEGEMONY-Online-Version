from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send
import 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

lobbies = {}

@socketio.on('connect')
def connect():
    print('Client connected with socket ID:', request.sid)

@socketio.on('disconnect')
def disconnet():
    print('Client disconnected with socket ID:', request.sid)

@socketio.on('createLobby')
def createLobby(data):
    print('Create lobby')
    print(data)
    lobbies[data] = data
    socketio.emit('lobbyCreated', data)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
