from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send
from string import ascii_uppercase
from game_state_manager import *

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Contains all lobbies
players = {}
lobbies = {}
SES = setup_event_scheduler()

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
    lobby['setup_mode'] = "all_manuel"
    print(lobby)

    # TEMP START GAME SEQUENCE | FOR TESTING ONLY
    lobby['waitlist'] = []
    lobby['map_name'] = 'MichaelMap1'
    player_list = [{'sid': pid, 'name': players[pid]['username']} for pid in lobby['players'] ]
    lobby['gsm'] = Game_State_Manager(lobby['map_name'], player_list, SES.get_event_scheduler(lobby['setup_mode']), socketio, lobby_id)

    socketio.emit('game_started', room=lobby_id)
    lobby['gsm'].run_setup_events()
    lobby['gsm'].run_turn_scheduler()

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
    lobby_map = lobby['gsm'].map
    # FILL IN MAP CHOSEN
    socketio.emit('game_settings',
     {'map': lobby['map_name'], 
    'tnames': lobby_map.tnames, 
    'tneighbors': lobby_map.tneighbors}, room=sid)

@socketio.on('send_color_choice')
def update_color_choice(data):
    color = data.get('choice')
    gsm = lobbies[players[request.sid]['lobby_id']]['gsm']
    if color not in gsm.made_choices:
        gsm.made_choices.append(color)
        gsm.aval_choices.remove(color)
        socketio.emit('color_picked', {'option': color}, room=players[request.sid]['lobby_id'])
        socketio.emit('clear_view', room=request.sid)
        gsm.players[request.sid].color = color
    else:
        socketio.emit('choose_color', {'msg': 'Choose a color to represent your country', 'options': gsm.aval_choices}, room=request.sid)

@socketio.on('send_dist_choice')
def update_dist_choice(data):
    dist = data.get('choice')
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.players[pid].territories = gsm.aval_choices[dist]
    del gsm.aval_choices[dist]
    gsm.server.emit('update_player_list', {'list': gsm.players[pid].territories}, room=pid)
    for trty in gsm.players[pid].territories:
        gsm.server.emit('update_trty_display', {trty: {'color': gsm.players[pid].color, 'troops': 1}}, room=gsm.lobby)
    gsm.selected = True

@socketio.on('send_capital_choice')
def update_player_capital(data):
    tid = data.get('tid')
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if tid in gsm.players[pid].territories:
        gsm.players[pid].capital = gsm.map.territories[tid].name # territory name instead of id
        gsm.map.territories[tid].isCapital = True
        gsm.server.emit('update_trty_display', {tid: {'isCapital': True}}, room=gsm.lobby)
        gsm.server.emit('capital_result', {'resp': True}, room=pid)
        return
    gsm.server.emit('capital_result', {'resp': False}, room=pid)

@socketio.on('send_city_choices')
def update_player_city(data):
    choices = data.get('choice')
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    for c in choices:
        if c not in gsm.players[pid].territories:
            gsm.server.emit('city_result', {'resp': False}, room=pid)
            return
    for trty in choices:
        gsm.map.territories[trty].isCity = True
        gsm.server.emit('update_trty_display', {trty: {'hasDev': 'city'}}, room=gsm.lobby)
    gsm.server.emit('city_result', {'resp': True}, room=pid)

@socketio.on('send_troop_update')
def update_troop_info(data):
    choice = data.get('choice')
    amount = int(data.get('amount'))
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if choice not in gsm.players[pid].territories:
        gsm.server.emit('troop_result', {'resp': False}, room=pid)
        return
    t = gsm.map.territories[choice]
    t.troops += amount
    gsm.players[pid].deployable_amt -= amount
    gsm.server.emit('update_trty_display',{choice:{'troops':t.troops}}, room=gsm.lobby)
    if gsm.players[pid].deployable_amt > 0:
        gsm.server.emit('troop_deployment', {'amount': gsm.players[pid].deployable_amt}, room=pid)
    else:
        gsm.server.emit('troop_result', {'resp': True}, room=pid)

@socketio.on('send_skill_choice')
def update_skill_choice(data):
    skill = data.get('choice')
    lobbies[players[request.sid]['lobby_id']]['gsm'].players[request.sid].skill = skill
    return

@socketio.on('send_battle_data')
def handle_battle(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.handle_battle(data)
    return

@socketio.on("get_reachable_trty")
def get_reachable_trty(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    reachable_trty = gsm.map.get_reachable_trty(data['choice'], gsm.players[pid].territories)
    gsm.server.emit('update_clickables', {'trtys': reachable_trty}, room=pid)

@socketio.on("terminate_conquer_stage")
def terminate_conquer_stage():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.turn_loop_scheduler.stage2 = True

@socketio.on("terminate_rearrangement_stage")
def terminate_rearrangement_stage():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.turn_loop_scheduler.stage3 = True

@socketio.on('send_rearrange_data')
def handle_rearrange_data(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    choices = data['choice']
    amount = int(data['amount'])
    t1 = gsm.map.territories[choices[0]]
    t2 = gsm.map.territories[choices[1]]
    t1.troops -= amount
    t2.troops += amount
    socketio.emit('update_trty_display', {
        choices[0]: {'troops': t1.troops},
        choices[1]: {'troops': t2.troops}
    } , room=gsm.lobby)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
