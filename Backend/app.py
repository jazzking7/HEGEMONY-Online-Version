from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from string import ascii_uppercase

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

lobbies = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in lobbies:
            break
    return code

@socketio.on('connect')
def connect(auth):
    print('Client connected with socket ID:', request.sid)

@socketio.on('disconnect')
def disconnet():
    print('Client disconnected with socket ID:', request.sid)

@socketio.on('createLobby')
def createLobby(data):
    print(f'{data.get("username")} is creating a lobby')
    socketio.emit('createLobby', data)

@socketio.on('lobbyCreation')
def lobbyCreation(data):
    print(data.get('username'))
    print(data.get('maxPlayers'))
    print(data.get('allianceOn'))
    print(data)
    socketio.emit('gameLobby', data)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
