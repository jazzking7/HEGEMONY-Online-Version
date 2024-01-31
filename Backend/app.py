from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from string import ascii_uppercase
from game_state_manager import *
import time
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Contains all lobbies
players = {}
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
def disconnect():
    sid = request.sid
    print('Client disconnected with socket ID:', sid)
    if not sid in players:
        return
    username = players[sid]['username']
    lobby_id = players[sid]['lobby_id']
    del players[sid]
    leave_room(lobby_id)
    if lobby_id is None:
        return
    lobby = lobbies[lobby_id]
    lobby['players'].remove(sid)
    if len(lobby['players']) == 0:
        del lobbies[lobby_id]
        return
    if lobby['host'] == sid:
        lobby['host'] = random.choice(lobby['players'])
        socketio.emit('update_lobby', {"event": "change_host", "target": lobby['host']}, room=lobby_id)
    socketio.emit('update_lobby', {"event": "disconnect", "target": username}, room=lobby_id)

### Main menu functions ###
    
@socketio.on('create_lobby')
def createLobby(data):
    print('create_lobby', data)
    sid = request.sid
    username = data.get('username')
    print(f'{username} is creating a lobby')    # TODO delete me
    lobby_code = generate_unique_code(5)
    players[request.sid] = {
        'username': username,
        'lobby_id': lobby_code
    }
    join_room(lobby_code)
    # TODO populate lobbies dict better
    lobbies[lobby_code] = {
        'host': sid,
        'players': [sid]
    }
    socketio.emit('lobby_created', room=sid)

@socketio.on('join_lobby')
def joinLobby(data):
    print('join_lobby', data)
    sid = request.sid
    username = data.get('username')
    lobby_code = data.get('lobby_code')

    # Check if lobby exists
    if lobby_code not in lobbies:
        print(f"ERROR: The lobby {lobby_code} does not exist!")
        socketio.emit('error', {'msg': "Invalid lobby code!"}, room=sid)
        return
    
    # Add player
    players[sid] = {
        'username': username,
        'lobby_id': lobby_code
    }

    # Add player to lobby
    lobby = lobbies[lobby_code]
    lobby['players'].append(sid)
    join_room(lobby_code)

    # Update lobby info
    socketio.emit('update_lobby', {"event": "join", "target": username}, room=lobby_code)
    socketio.emit('lobby_joined', room=sid)

### Lobby functions ###

@socketio.on('get_lobby_data')
def get_lobby_data():
    sid = request.sid
    if sid not in players:
        return
    lobby_id = players[sid]['lobby_id']
    if lobby_id is None:
        return
    lobby = lobbies[lobby_id]
    lobby_players = []
    for player_sid in lobby['players']:
        lobby_players.append(players[player_sid]['username'])
    out_data = {
        'host': lobby['host'],
        'lobby_id': lobby_id,
        'players': lobby_players
    }
    socketio.emit('lobby_data', out_data, room=sid)

@socketio.on('start_game')
def startGame(data):
    sid = request.sid
    lobby_id = players[sid]['lobby_id']
    lobby = lobbies[lobby_id]

    # Safeguard
    if lobby['host'] != sid:
        socketio.emit('error', {'msg': "Only the host can start the game!"}, room=sid)
        return
    if len(lobby['players']) < 1:   # TODO testing only - setup a constant
        socketio.emit('error', {'msg': "Not enough players!"}, room=sid)
        return
    
    # Setup lobby settings ## TO BE UPDATED
    lobby['alliance'] = data.get('alliance')
    lobby['turn_time'] = int(data.get('turn_time'))
    print(lobby)

    # TEMP START GAME SEQUENCE | FOR TESTING ONLY
    lobby['waitlist'] = []
    lobby['map_name'] = 'MichaelMap1'
    lobby['map'] = Map(lobby['map_name'])

    socketio.emit('game_started', room=lobby_id)

### Game functions ###

## SET UP 
@socketio.on('get_game_settings')
def get_game_settings():
    sid = request.sid
    if sid not in players:
        return
    lobby_id = players[sid]['lobby_id']
    if lobby_id is None:
        return
    lobby = lobbies[lobby_id]
    lobby_map = lobby['map']
    # FILL IN MAP CHOSEN
    socketio.emit('game_settings',
     {'map': lobby['map_name'], 
    'tnames': lobby_map.tnames, 
    'tneighbors': lobby_map.tneighbors}, room=sid)

@socketio.on('clicked')
def handle_clicks(data):
    print(f'{request.sid} has clicked on {data.get("id")}')
    return


@socketio.on('send_color_choice')
def update_color_choice(data):
    color = data.get('choice')
    # MAKE SURE COLOR NOT CHOSEN
    socketio.emit('color_picked', {'option': color}, room=players[request.sid]['lobby_id'])

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
