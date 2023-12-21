from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from string import ascii_uppercase

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Contains all lobbies
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
    socketio.emit('createLobby', data, room=request.sid)

@socketio.on('lobbyCreation')
def lobbyCreation(data):
    print(data)
    allianceOn = data.get('allianceOn') == "yes"
    # Create lobby
    lobby_code = generate_unique_code(5)
    lobbies[lobby_code] = {
        'lobby_code': lobby_code,
        'players': [data.get('username')],
        'maxPlayers': int(data.get('maxPlayers')),
        'numPlayersIn': 1,
        'allianceOn': allianceOn}
    join_room(lobby_code)
    socketio.emit('gameLobby', lobbies[lobby_code], room=lobby_code)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
