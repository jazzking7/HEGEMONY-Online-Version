import random
import time
import json
import math
import threading

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
    
    # MISSION DISTRIBUTION
    def distribute_missions(self, gs, ms):
        # CM
        miss_set = gs.Mdist.get_mission_set(len(gs.pids))
        for index, player in enumerate(gs.pids):
            miss_set[index] = gs.Mdist.initiate_mission(gs, player, miss_set[index])

        # Set up mission trackers for all missions
        gs.Mdist.set_up_mission_trackers(gs, miss_set)
        gs.Mset = miss_set 

        # Set up partner for loyalist
        for m in gs.Mset:
            if m.name == "Loyalist":
                m.set_partner()
            elif m.name == "Fanatic":
                m.set_targets()
            elif m.name == 'Duelist':
                m.set_nemesis()
            elif m.name == 'Assassin':
                m.set_targets()
            elif m.name == 'Protectionist':
                m.set_targets()

        # Set up user view for mission
        for mission in gs.Mset:
            mission.set_up_tracker_view()
            gs.server.emit('get_mission', {'msg': f'Your agenda: {mission.name}'}, room=mission.player)

        ms.selection_time_out(20, len(gs.players))

    # FCFS
    def start_color_distribution(self, gs, ms):
        gs.aval_choices = []
        with open('Setting_Options/colorOptions.json') as file:
            color_options = json.load(file)
        gs.aval_choices = color_options
        for player in gs.players:
            gs.server.emit('choose_color', {'msg': 'Choose a color to represent your country', 'options': color_options}, room=player)
        
        ms.selection_time_out(30, len(gs.players))

        # handle timeout
        for player in gs.players.values():
            # CM
            if player.color is None:
                print("Did not choose a color!")
                player.color = random.choice(gs.aval_choices)
                gs.aval_choices.remove(player.color)
        gs.signal_view_clear()
        gs.made_choices = []
        gs.color_options = gs.aval_choices
        gs.made_choices = []
        gs.send_player_list()

    # TURN-BASED
    def start_territorial_distribution(self,gs, ms):
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

            for reci in gs.players:
                if reci != player:
                    gs.server.emit('set_up_announcement', {'msg': f"Select territorial distribution: {gs.players[player].name} is choosing"}, room=reci)
                else:
                    gs.server.emit('set_up_announcement', {'msg': f"Select a territorial distribution"}, room=player)
            gs.server.emit('choose_territorial_distribution', {'options': gs.aval_choices}, room=player)
            

            ms.selection_time_out(ms.trty_set_time, 1)
            
            # handle timeout
            if not ms.selected:
                # CM
                print("Did not choose a distribution!")
                random_key, random_dist = random.choice(list(gs.aval_choices.items()))
                gs.players[player].territories = random_dist
                gs.server.emit('update_player_territories', {'list': gs.players[player].territories}, room=player)
                del gs.aval_choices[random_key]
                for trty in random_dist:
                    gs.server.emit('update_trty_display', {trty:{'color': gs.players[player].color, 'troops': 1}}, room=gs.lobby) 
                gs.server.emit('clear_view', room=player)
        gs.aval_choices = []
    
    def start_capital_settlement(self, gs, ms):
        gs.server.emit('set_up_announcement', {'msg':f"Settle your capital!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_capital"}, room=gs.lobby)

        ms.selection_time_out(ms.trty_set_time, len(gs.players))

        # handle not choosing
        for player in gs.players.values():
            # CM
            if player.capital == None:
                print("Did not choose a capital!")
                capital = random.choice(player.territories)
                gs.map.territories[capital].isCapital = True
                player.capital = gs.map.territories[capital].name
                gs.server.emit('update_trty_display', {capital:{'isCapital': True, 'capital_color': player.color}}, room=gs.lobby)
                gs.server.emit('capital_result', {'resp': True}, room=gs.lobby)
        gs.signal_view_clear()
    
    def start_city_settlement(self,gs, ms):
        gs.server.emit('set_up_announcement', {'msg':f"Build up two cities!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_cities"}, room=gs.lobby)

        ms.selection_time_out(ms.trty_set_time, len(gs.players))


        for player in gs.players.values():
            # CM
            if gs.map.count_cities(player.territories) == 0:
                print("Did not choose cities!")
                cities = random.sample(player.territories, k=2)
                for c in cities:
                    gs.map.territories[c].isCity = True
                    gs.server.emit('update_trty_display', {c:{'hasDev': 'city'}}, room=gs.lobby)
                    gs.server.emit('city_result', {'resp': True}, room=gs.lobby)
        gs.signal_view_clear()
    
    def start_initial_deployment(self, gs, ms):
        gs.server.emit('change_click_event', {'event': "troop_deployment"}, room=gs.lobby)
        gs.reverse_players()
        curr = 0
        for player in gs.players:
            amount = len(gs.players[player].territories) + (curr*3) + (curr//2)
            curr += 1
            gs.players[player].deployable_amt = amount
            gs.server.emit('troop_deployment', {'amount': amount}, room=player)

        ms.selection_time_out(ms.power_set_time, len(gs.players))

        gs.signal_view_clear()
        gs.server.emit('change_click_event', {'event': None}, room=gs.lobby)
        gs.server.emit('troop_result', {'resp': True}, room=gs.lobby)
        time.sleep(3)
        for player in gs.players:
            gs.clear_deployables(player)
    
    def start_skill_selection(self, gs, ms):
        gs.server.emit('set_up_announcement', {'msg': "Choose your Ultimate War Art"}, room=gs.lobby)
        for player in gs.players:
            options = gs.SDIS.get_options() if player != gs.annilator else gs.SDIS.get_annilator_options()
            gs.server.emit('choose_skill', {'options': options}, room=player)

        ms.selection_time_out(ms.power_set_time, len(gs.players))

        gs.signal_view_clear()

        for player in gs.players:
            # CM
            if not gs.players[player].skill:
                # Randomly assign mission to player
                gs.players[player].skill = gs.SDIS.initiate_skill(gs.SDIS.get_single_option(), player, gs)