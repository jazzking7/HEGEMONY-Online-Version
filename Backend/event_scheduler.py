import random
import time
import json
import math
import threading

class Event:
    def __init__(self, name, event,):
        self.name = name
        self.executable = event

class turn_loop_scheduler:

    # current_player -> index
    # curr_player refers to pid corresponding to the current_player

    def __init__(self, ):
        self.events = [
            Event("reinforcement", self.reinforcement),
            Event("conquer", self.conquer),
            Event("rearrangement", self.rearrange)
        ]
        # loop interrupted
        self.interrupt = False
        # current turn terminated
        self.terminated = False
        # stage gate
        self.stage_completed = False
        # current round
        self.round = 0
        # thread for turn execution
        self.curr_thread = None
        # thread for timer
        self.timer = None
        # current event
        self.current_event = None
        self.current_player = 0
        # stack of events in case of interruption
        self.event_stack = []

    def set_curr_stat(self, gs, event):
        gs.current_event = event
        return

    def activate_timer(self, num_secs):
        sec = 0
        while not self.terminated and sec < num_secs:
            time.sleep(1)
            sec += 1
            print(sec)
        self.stage_completed = True
        self.terminated = True
        return

    def reinforcement(self, gs, curr_p):
        for player in gs.pids:
            if player != curr_p:
                gs.server.emit('set_up_announcement', {'msg': f"{gs.players[curr_p].name}'s turn: reinforcement"}, room=player)
        gs.server.emit('change_click_event', {'event': "troop_deployment"}, room=curr_p)
        gs.players[curr_p].deployable_amt = gs.get_deployable_amt(curr_p) 
        gs.server.emit("troop_deployment", {'amount': gs.players[curr_p].deployable_amt}, room=curr_p)
        return

    def conquer(self, gs, curr_player):
        gs.server.emit('set_up_announcement', {'msg': f"{gs.players[curr_player].name}'s turn: conquest"}, room=gs.lobby)
        gs.server.emit("change_click_event", {'event': 'conquest'}, room=curr_player)
        gs.server.emit("conquest", room=curr_player)
        return
    
    def rearrange(self, gs, curr_player):
        gs.server.emit('set_up_announcement', {'msg': f"{gs.players[curr_player].name}'s turn: rearrangement"}, room=gs.lobby)
        gs.server.emit("change_click_event", {'event': 'rearrange'}, room=curr_player)
        gs.server.emit("rearrangement", room=curr_player)
        return

    def execute_turn_events(self, gs, player):

        atk_player = gs.players[player]
        atk_player.turn_victory = False

        self.set_curr_stat(gs, self.events[0])
        self.reinforcement(gs, player)
        self.stage_completed = False
        done = False
        while not self.stage_completed and not done:
            done = atk_player.deployable_amt == 0
        if self.terminated:
            return

        self.set_curr_stat(gs, self.events[1])
        # Prevent Immediate Stats growth
        atk_player.temp_stats = gs.get_player_battle_stats(atk_player)
        self.conquer(gs, player)
        self.stage_completed = False
        while not self.stage_completed:
            time.sleep(1)
        if self.terminated:
            return
        
        self.set_curr_stat(gs, self.events[2])
        self.rearrange(gs, player)
        self.stage_completed = False
        while not self.stage_completed:
            time.sleep(1)
        if self.terminated:
            return
        # stop timer
        self.terminated = True
        return
    
    def handle_end_turn(self, gs, player):
        # notify frontend to change event and clear controls
        gs.server.emit("change_click_event", {'event': None}, room=player)
        gs.server.emit("clear_view", room=player)
        # clear deployables
        gs.clear_deployables(player)
        # assign stars if applicable
        p = gs.players[player]
        if p.turn_victory:
            p.stars += random.choices([1,2,3],[0.3, 0.4, 0.3],k=1)[0]
        print(p.stars)

    def execute_turn(self, gs, curr_player):

        self.curr_thread = threading.Thread(target=self.execute_turn_events, args=(gs, curr_player))
        self.timer = threading.Thread(target=self.activate_timer, args=(30,))

        self.terminated = False
        self.curr_thread.start()

        gs.server.emit('start_timeout',{'secs': 30}, room=gs.lobby)
        self.timer.start()
        self.timer.join()
        gs.server.emit('stop_timeout', room=gs.lobby)
        
        self.curr_thread.join()

        self.handle_end_turn(gs, curr_player)

    def run_turn_loop(self, gs):
        curr_player = gs.pids[self.current_player]
        while not self.interrupt:
            if gs.players[curr_player].alive:
                self.execute_turn(gs, curr_player)
            self.current_player += 1
            if self.current_player == len(gs.pids):
                self.current_player = 0
                self.round += 1
            curr_player = gs.pids[self.current_player]
            
class setup_event_scheduler:
    def __init__(self, ):
        self.events = [
            Event("give_mission", self.distribute_missions),
            Event("choose_color", self.start_color_distribution),
            Event("choose_distribution", self.start_territorial_distribution),
            Event("choose_capital", self.start_capital_settlement),
            Event("set_cities", self.start_city_settlement),
            Event("initial_deployment", self.start_initial_deployment),
            Event("choose_skill", self.start_skill_selection)
        ]

    # ADD OPTIONS FOR AUTO_TRTY, FULL_AUTO
    def get_event_scheduler(self, setup_mode):
        event_list = []
        if setup_mode == "all_manuel":
            for event in self.events:
                event_list.append(event)
            return event_list
    
    # TO BE UPDATED
    def distribute_missions(self, gs):
        for player in gs.players:
            continents = ['Pannotia', 'Zealandia', 'Baltica', 'Rodinia', 'Kenorland', 'Kalahari']
            gs.server.emit('get_mission', {'msg': f'Mission: capture {random.choice(continents)}'}, room=player)
            
        gs.set_time_out(5)

    # FCFS
    def start_color_distribution(self, gs):
        gs.aval_choices = []
        with open('Setting_Options/colorOptions.json') as file:
            color_options = json.load(file)
        gs.aval_choices = color_options
        for player in gs.players:
            gs.server.emit('choose_color', {'msg': 'Choose a color to represent your country', 'options': color_options}, room=player)
        
        gs.set_time_out(5)

        # handle timeout
        for player in gs.players.values():
            if player.color is None:
                print("Did not choose a color!")
                player.color = random.choice(gs.aval_choices)
                gs.aval_choices.remove(player.color)
        gs.signal_view_clear()
        gs.made_choices = []
        gs.color_options = gs.aval_choices
        gs.made_choices = []

    # TURN-BASED
    def start_territorial_distribution(self,gs):
        gs.aval_choices = {}
        choices = random.sample(gs.color_options, k=len(gs.players))
        gs.shuffle_players()
        # RANDOM TRTY DISTRIBUTION
        avg_num_trty = math.floor(len(gs.map.tnames)/len(gs.players))
        trty_list = [i for i in range(len(gs.map.tnames))]
        for choice in choices:
            curr_dist = []
            while(len(curr_dist) < avg_num_trty):
                tmp = random.choice(trty_list)
                trty_list.remove(tmp)
                curr_dist.append(tmp)
            gs.aval_choices[choice] = curr_dist
        curr_i = 0
        while(len(trty_list) != 0):
            tmp = random.choice(trty_list)
            gs.aval_choices[choices[curr_i]].append(tmp)
            trty_list.remove(tmp)
            curr_i+=1
        # UPDATE TRTY VIEW
        for dist in gs.aval_choices:
            for trty in gs.aval_choices[dist]:
                gs.server.emit('update_trty_display', {trty:{'color': dist}}, room=gs.lobby) 
        # NOTIF EVENT ONE BY ONE
        for player in gs.players:
            gs.selected = False
            for reci in gs.players:
                if reci != player:
                    gs.server.emit('set_up_announcement', {'msg': f"Select territorial distribution: {gs.players[player].name} is choosing"}, room=reci)
                else:
                    gs.server.emit('set_up_announcement', {'msg': f"Select a territorial distribution"}, room=player)
            gs.server.emit('choose_territorial_distribution', {'options': gs.aval_choices}, room=player)
            
            gs.set_time_out(5)
            
            # handle timeout
            if not gs.selected:
                print("Did not choose a distribution!")
                random_key, random_dist = random.choice(list(gs.aval_choices.items()))
                gs.players[player].territories = random_dist
                gs.server.emit('update_player_list', {'list': gs.players[player].territories}, room=player)
                del gs.aval_choices[random_key]
                for trty in random_dist:
                    gs.server.emit('update_trty_display', {trty:{'color': gs.players[player].color, 'troops': 1}}, room=gs.lobby) 
                gs.server.emit('clear_view', room=player)
        gs.aval_choices = []
    
    def start_capital_settlement(self, gs):
        gs.server.emit('set_up_announcement', {'msg':f"Settle your capital!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_capital"}, room=gs.lobby)

        gs.set_time_out(5)

        # handle not choosing
        for player in gs.players.values():
            if player.capital == None:
                print("Did not choose a capital!")
                player.capital = random.choice(player.territories)
                gs.map.territories[player.capital].isCapital = True
                gs.server.emit('update_trty_display', {player.capital:{'isCapital': True}}, room=gs.lobby)
                gs.server.emit('capital_result', {'resp': True}, room=gs.lobby)
        gs.signal_view_clear()
    
    def start_city_settlement(self,gs):
        gs.server.emit('set_up_announcement', {'msg':f"Build up two cities!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_cities"}, room=gs.lobby)

        gs.set_time_out(5)


        for player in gs.players.values():
            if gs.map.count_cities(player.territories) == 0:
                print("Did not choose cities!")
                cities = random.sample(player.territories, k=2)
                for c in cities:
                    gs.map.territories[c].isCity = True
                    gs.server.emit('update_trty_display', {c:{'hasDev': 'city'}}, room=gs.lobby)
                    gs.server.emit('city_result', {'resp': True}, room=gs.lobby)
        gs.signal_view_clear()
    
    def start_initial_deployment(self,gs):
        gs.shuffle_players()
        gs.server.emit('change_click_event', {'event': "troop_deployment"}, room=gs.lobby)
        curr = 0
        for player in gs.players:
            amount = len(gs.players[player].territories) + 5
            if (curr >= len(gs.players)//2):
                amount += 3
            curr += 1
            gs.players[player].deployable_amt = amount
            gs.server.emit('troop_deployment', {'amount': amount}, room=player)

        gs.set_time_out(5)

        gs.signal_view_clear()
        gs.server.emit('change_click_event', {'event': None}, room=gs.lobby)
        gs.server.emit('troop_result', {'resp': True}, room=gs.lobby)
        time.sleep(2)
        for player in gs.players:
            gs.clear_deployables(player)
    
    def start_skill_selection(self,gs):
        gs.server.emit('set_up_announcement', {'msg': "Choose your Ultimate War Art"}, room=gs.lobby)
        for player in gs.players:
            options = random.sample(gs.skill_options, k=5)
            gs.server.emit('choose_skill', {'options': options}, room=player)

        gs.set_time_out(5)

        gs.signal_view_clear()
        for player in gs.players:
            if gs.players[player].skill == None:
                gs.players[player].skill = random.choice(gs.skill_options)