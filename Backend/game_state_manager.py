# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
# Player Object
# Game Object
# World Status Display
import random
import time
import json
import math
from game_map import *

class Player:

    def __init__(self, name, G):
        # identity
        self.name = name
        # status
        self.alive = True
        # agenda
        self.mission = None
        # skill
        self.skill = None
        # ownership
        self.territories = []
        self.capital = None
        # battle stats
        self.industrial = 6
        self.infrastructure = 3
        self.infrastructure_upgrade = 0
        # hidden resources
        self.stars = 0
        self.reserves = 0
        # alliance
        self.hasAllies = False
        self.allies = []
        self.ally_socket = None
        # turn
        self.conquered = False
        self.game = G
        # visuals
        self.color = None
        self.insignia = None
        # puppet state
        self.puppet = False
        self.master = None
        self.vassals = []
        # deployment
        self.deployable_amt = 0
        # economy
        self.cumulative_gdp = 0

class Event:
    def __init__(self, name, event,):
        self.name = name
        self.executable = event

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
        time.sleep(1)

    # FCFS
    def start_color_distribution(self, gs):
        gs.aval_choices = []
        with open('Setting_Options/colorOptions.json') as file:
            color_options = json.load(file)
        gs.aval_choices = color_options
        for player in gs.players:
            gs.server.emit('choose_color', {'msg': 'Choose a color to represent your country', 'options': color_options}, room=player)
        time.sleep(10)
        # handle timeout
        for player in gs.players.values():
            if player.color is None:
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
        trty_list = gs.map.tnames[:]
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
            time.sleep(10)
            # handle timeout
            if not gs.selected:
                random_key, random_dist = random.choice(list(gs.aval_choices.items()))
                gs.players[player].territories = random_dist
                del gs.aval_choices[random_key]
                for trty in random_dist:
                    gs.server.emit('update_trty_display', {trty:{'color': gs.players[player].color, 'troops': 1}}, room=gs.lobby) 
                gs.server.emit('clear_view', room=player)
                print("NOT CHOSEN")
        gs.aval_choices = []
    
    def start_capital_settlement(self, gs):
        gs.server.emit('set_up_announcement', {'msg':f"Settle your capital!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_capital"}, room=gs.lobby)
        time.sleep(15)
        # handle not choosing
        for player in gs.players.values():
            if player.capital == None:
                player.capital = random.choice(player.territories)
                gs.map.get_trty(player.capital).isCapital = True
                gs.server.emit('update_trty_display', {player.capital:{'isCapital': True}}, room=gs.lobby)
                gs.server.emit('capital_result', {'resp': True}, room=gs.lobby)
        gs.signal_view_clear()
    
    def start_city_settlement(self,gs):
        gs.server.emit('set_up_announcement', {'msg':f"Build up two cities!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_cities"}, room=gs.lobby)
        time.sleep(15)
        for player in gs.players.values():
            if gs.map.count_cities(player.territories) == 0:
                cities = random.sample(player.territories, k=2)
                for c in cities:
                    gs.map.get_trty(c).isCity = True
                    gs.server.emit('update_trty_display', {c:{'hasDev': 'city'}}, room=gs.lobby)
                    gs.server.emit('city_result', {'resp': True}, room=gs.lobby)
        gs.signal_view_clear()
    
    def start_initial_deployment(self,gs):
        gs.shuffle_players()
        gs.server.emit('change_click_event', {'event': "troop_deployment"}, room=gs.lobby)
        curr = 0
        for player in gs.players:
            amount = len(gs.players[player].territories) + 5
            if (curr > len(gs.players)//2):
                amount += 3
            gs.players[player].deployable_amt = amount 
            gs.server.emit('troop_deployment', {'amount': amount}, room=player)
        time.sleep(20)
        gs.signal_view_clear()
        gs.server.emit('change_click_event', {'event': None}, room=gs.lobby)
        gs.server.emit('troop_result', {'resp': True}, room=gs.lobby)
        time.sleep(2)
        for player in gs.players:
            p =  gs.players[player]
            if p.deployable_amt > 0:
                while (p.deployable_amt != 0):
                    trty = random.choice(p.territories)
                    t = gs.map.get_trty(trty)
                    t.troops += 1
                    p.deployable_amt -= 1
                    gs.server.emit('update_trty_display', {trty:{'troops': t.troops}}, room=gs.lobby)
    
    def start_skill_selection(self,gs):
        gs.server.emit('set_up_announcement', {'msg': "Choose your Ultimate War Art"}, room=gs.lobby)
        for player in gs.players:
            options = random.sample(gs.skill_options, k=5)
            gs.server.emit('choose_skill', {'options': options}, room=player)
        time.sleep(15)
        gs.signal_view_clear()
        for player in gs.players:
            if gs.players[player].skill == None:
                gs.players[player].skill = random.choice(gs.skill_options)

class Game_State_Manager:

    def __init__(self, mapName, player_list, setup_events, server, lobby):

        # Number of players and players are related
        self.players = {}
        for player in player_list:
            self.players[player['sid']] = Player(player['name'], self)

        # Map
        self.map = Map(mapName)
        self.total_troops = len(self.map.territories)

        # turn counter
        self.turn = 0
        self.stage = 0

        # max number of allies allowed in an alliance
        self.max_allies = 2
        
        # loop elements update on async
        self.curr_reinforcer = None
        self.curr_conqueror = None
        
        # SELECTION TRACKER
        self.aval_choices = []
        self.made_choices = []
        self.selected = True

        # color options
        self.color_options = []
        # skill options
        self.skill_options = [
            "Sturdy_As_Steel",
            "Usurper",
            "Air_Superiority",
            "Divine_Punishment",
            "Industrial_Revolution",
            "Zealous_Expansion",
            "Mass_Mobilization",
            "Handler_of_Wheel_of_Fortune",
            "Laplace_Demon",
            "Necromancer",
            "Ares_Blessing",
            "Dictator"
        ]

        # server
        self.server = server
        self.lobby = lobby

        # EVENT SCHEDULERS
        self.round = 0
        self.current_event = None
        self.setup_scheduler = setup_events
    
    def run_game_events(self,):
        time.sleep(3)
        for event in self.setup_scheduler:
            event.executable(self)

    def shuffle_players(self, ):
        shuffled_keys = list(self.players.keys())
        random.shuffle(shuffled_keys)
        shuffled_dict = {key: self.players[key] for key in shuffled_keys}
        self.players = shuffled_dict
        for player in self.players:
            self.server.emit('update_player_info', room=player)

    def signal_view_clear(self,):
        for player in self.players:
            self.server.emit('clear_view', room=player)