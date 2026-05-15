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
            # Event("choose_color", self.start_color_distribution),
            Event("choose_distribution", self.start_territorial_distribution),
            Event("choose_capital", self.start_capital_settlement),
            Event("set_cities", self.start_city_settlement),
            Event("initial_deployment", self.start_initial_deployment),
            Event("choose_skill", self.start_skill_selection)
        ]

        self.QS = [
            Event("give_mission", self.distribute_missions),
            Event("quick_setup", self.quick_setup),
            Event("choose_skill", self.start_skill_selection),
        ]

    # ADD OPTIONS FOR AUTO_TRTY, FULL_AUTO
    def get_event_scheduler(self, setup_mode):
        event_list = []
        if setup_mode == "all_manuel":
            for event in self.events:
                event_list.append(event)
            return event_list
        if setup_mode == "quicksetup":
            for event in self.QS:
                event_list.append(event)
            return event_list
        
    def quick_setup(self, gs, ms):
        # ── 1. Shuffle player queue ──
        gs.shuffle_players()

        # ── 2. Generate random territory distributions ──
        choices = gs.colorSets[len(gs.players)]

        avg_num_trty = math.floor(len(gs.map.tnames) / len(gs.players))
        trty_list    = list(range(len(gs.map.tnames)))

        distributions = {}   # color -> list of tids
        for choice in choices:
            curr_dist = []
            while len(curr_dist) < avg_num_trty:
                tmp = random.choice(trty_list)
                trty_list.remove(tmp)
                curr_dist.append(tmp)
            distributions[choice] = curr_dist

        curr_i = 0
        while trty_list:
            tmp = random.choice(trty_list)
            distributions[choices[curr_i]].append(tmp)
            trty_list.remove(tmp)
            curr_i = (curr_i + 1) % len(choices)

        # ── 3. Randomly assign distributions to players ──
        color_pool = list(choices)
        random.shuffle(color_pool)
        player_color = {}   # pid -> color
        for pid in gs.players:
            color = color_pool.pop()
            player_color[pid] = color

        # ── 4. Assign territories and color to each player ──
        for pid in gs.players:
            color = player_color[pid]
            player = gs.players[pid]
            player.color       = color
            player.territories = distributions[color]
            player.total_troops = len(player.territories)

            for trty in player.territories:
                gs.server.emit('update_trty_display', {trty: {'color': color, 'troops': 1}}, room=gs.lobby)

            gs.server.emit('update_player_territories', {'list': player.territories}, room=pid)

        gs.server.emit('rebuild_mapshape_cache', room=gs.lobby)

        # ── 5. Set capital for each player using bot logic ──
        # Borrow a bot ref just for its scoring methods.
        # We swap .territories and .color temporarily, restore after each call.
        bot_ref = None
        for pid in gs.pids:
            if gs.players[pid].isBot:
                bot_ref = gs.players[pid]
                break
        if bot_ref is None:
            from botplayer import Botplayer as _BP
            bot_ref             = _BP.__new__(_BP)
            bot_ref.gs          = gs
            bot_ref.territories = []
            bot_ref.color       = None
            bot_ref.grudges     = {}
            bot_ref.allies      = []
            bot_ref.agenda      = ""

        for pid in gs.players:
            player = gs.players[pid]
            _save_terr, _save_color = bot_ref.territories, bot_ref.color
            bot_ref.territories = player.territories
            bot_ref.color       = player.color

            capital_tid = bot_ref.get_best_defendable_territory(player.territories)
            if capital_tid is None:
                capital_tid = random.choice(player.territories)

            bot_ref.territories, bot_ref.color = _save_terr, _save_color

            player.capital = gs.map.territories[capital_tid].name
            gs.map.territories[capital_tid].isCapital = True
            gs.server.emit('update_trty_display', {capital_tid: {'isCapital': True, 'capital_color': player.color}}, room=gs.lobby)

        # ── 6. Set 2 cities per player using bot logic ──
        for pid in gs.players:
            player = gs.players[pid]
            _save_terr, _save_color = bot_ref.territories, bot_ref.color
            bot_ref.territories = player.territories
            bot_ref.color       = player.color

            city_tids = bot_ref.get_best_territories_to_build(2, "city")

            # Fallback if scoring returns fewer than 2
            if len(city_tids) < 2:
                remaining = [t for t in player.territories
                             if not gs.map.territories[t].isCapital
                             and not gs.map.territories[t].isCity
                             and t not in city_tids]
                random.shuffle(remaining)
                for t in remaining:
                    if len(city_tids) >= 2:
                        break
                    city_tids.append(t)

            bot_ref.territories, bot_ref.color = _save_terr, _save_color

            for tid in city_tids:
                gs.map.territories[tid].isCity = True
                gs.server.emit('update_trty_display', {tid: {'hasDev': 'city'}}, room=gs.lobby)

        gs.server.emit('cityBuildingSFX', room=gs.lobby)

        # ── 7. Deploy initial troops — later players get more (mirrors start_initial_deployment) ──
        player_list = list(gs.players.keys())
        for idx, pid in enumerate(player_list):
            player     = gs.players[pid]
            deploy_amt = len(player.territories) + (idx * 3) + (idx // 2)

            # Find this player's capital and cities
            capital_tid = None
            city_tids   = []
            for tid in player.territories:
                t = gs.map.territories[tid]
                if t.isCapital and t.name == player.capital:
                    capital_tid = tid
                elif t.isCity:
                    city_tids.append(tid)

            has_capital = capital_tid is not None
            has_cities  = len(city_tids) > 0

            if has_capital and has_cities:
                capital_share = deploy_amt // (1 + len(city_tids))
                cities_share  = deploy_amt - capital_share
            elif has_capital:
                capital_share, cities_share = deploy_amt, 0
            elif has_cities:
                capital_share, cities_share = 0, deploy_amt
            else:
                continue

            if has_capital:
                gs.map.territories[capital_tid].troops += capital_share
                gs.server.emit('troop_addition_display', {f'{capital_tid}': {'tid': capital_tid, 'number': capital_share}}, room=gs.lobby)
                gs.server.emit('update_trty_display', {capital_tid: {'troops': gs.map.territories[capital_tid].troops}}, room=gs.lobby)

            if has_cities:
                per_city      = cities_share // len(city_tids)
                city_leftover = cities_share - (per_city * len(city_tids))

                for tid in city_tids:
                    gs.map.territories[tid].troops += per_city
                    gs.server.emit('troop_addition_display', {f'{tid}': {'tid': tid, 'number': per_city}}, room=gs.lobby)
                    gs.server.emit('update_trty_display', {tid: {'troops': gs.map.territories[tid].troops}}, room=gs.lobby)

                if city_leftover > 0:
                    target_tid = capital_tid if has_capital else city_tids[0]
                    gs.map.territories[target_tid].troops += city_leftover
                    gs.server.emit('troop_addition_display', {f'{target_tid}': {'tid': target_tid, 'number': city_leftover}}, room=gs.lobby)
                    gs.server.emit('update_trty_display', {target_tid: {'troops': gs.map.territories[target_tid].troops}}, room=gs.lobby)

            player.total_troops += deploy_amt

        # ── 8. Announce and highlight — all at once, 20s timer ──
        for pid in gs.players:
            player = gs.players[pid]
            gs.server.emit('set_new_announcement', {
                'async': True,
                'msg': f'You are controlling <span style="display:inline-block;width:20px;height:20px;background:{player.color};border:1px solid #fff;vertical-align:middle;border-radius:2px; margin-right:3px;"></span>. Take a look at your territories.'
            }, room=pid)

        gs.server.emit('quick_setup_highlight_on', room=gs.lobby)
        gs.server.emit('start_timeout', {'secs': 20}, room=gs.lobby)
        gs.server.sleep(20)
        gs.server.emit('stop_timeout', room=gs.lobby)

        gs.send_player_list()
        for pid in gs.players:
            gs.server.emit('initiate_chatboxes', {
                'colors': [gs.players[r].color for r in gs.players if r != pid]
            }, room=pid)

        gs.signal_view_clear()
    
    # MISSION DISTRIBUTION
    def distribute_missions(self, gs, ms):
        # CM
        num_bots = sum(1 for p in gs.pids if gs.players[p].isBot)

        if num_bots > 0:
            # Separate bot and human pids, bots get assigned first
            bot_pids     = [p for p in gs.pids if gs.players[p].isBot]
            human_pids   = [p for p in gs.pids if not gs.players[p].isBot]
            ordered_pids = bot_pids + human_pids
            miss_set     = gs.Mdist.get_mission_set_with_bots(len(gs.pids), num_bots, gs.complexity)
        else:
            ordered_pids = gs.pids
            miss_set     = gs.Mdist.get_mission_set(len(gs.pids), gs.complexity)

        for index, player in enumerate(ordered_pids):
            miss_set[index] = gs.Mdist.initiate_mission(gs, player, miss_set[index])
            if gs.players[player].isBot:
                gs.players[player].agenda             = miss_set[index]
                gs.players[player].growth_expectation = len(gs.map.territories) // (len(gs.players) + 2)

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
            gs.server.emit('set_new_announcement', {'async': True, 'msg': f'Your agenda: {mission.name}'}, room=mission.player)
            gs.server.emit('set_agenda_explanation', {"objective": mission.objective, "priority": mission.priority}, room=mission.player)
        ms.selection_time_out(10, len(gs.players))
        gs.server.emit('clear_middle_content', room=gs.lobby)

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
        # choices = random.sample(gs.color_options, k=len(gs.players))
        choices = gs.colorSets[len(gs.players)]
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
                    gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"Select territorial distribution: {gs.players[player].name} is choosing"}, room=reci)
                else:
                    gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"Select a territorial distribution"}, room=player)
            gs.server.emit('choose_territorial_distribution', {'options': gs.aval_choices}, room=player)
            

            # bot makes decision
            if gs.players[player].isBot:
                gs.server.emit('start_timeout',{'secs': ms.trty_set_time}, room=gs.lobby)
                gs.players[player].choose_territory()
                gs.server.emit('stop_timeout', room=gs.lobby)
            else:
            # human makes decision 
                ms.selection_time_out(ms.trty_set_time, 1)
            
            # handle timeout
            if not ms.selected:
                # CM
                print("Did not choose a distribution!")
                random_key, random_dist = random.choice(list(gs.aval_choices.items()))
                gs.players[player].color = random_key
                gs.players[player].territories = random_dist
                gs.server.emit('update_player_territories', {'list': gs.players[player].territories}, room=player)
                del gs.aval_choices[random_key]
                for trty in random_dist:
                    gs.server.emit('update_trty_display', {trty:{'color': gs.players[player].color, 'troops': 1}}, room=gs.lobby)
                gs.server.emit('clear_view', room=player)
        gs.aval_choices = []
        gs.send_player_list()
        for player in gs.players:
            gs.server.emit('initiate_chatboxes', {
                'colors': [gs.players[recipient].color for recipient in gs.players if recipient != player]
            }, room=player)
    
    def start_capital_settlement(self, gs, ms):
        gs.server.emit('set_new_announcement', {'async' : True, 'msg':f"Settle your capital!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_capital"}, room=gs.lobby)

        if gs.hasBot:
            ms.selection_time_out_with_bot(ms.trty_set_time, len(gs.players), 'set_capital')
        else:
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
        gs.server.emit('set_new_announcement', {'async' : True, 'msg':f"Build up two cities!"}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': "settle_cities"}, room=gs.lobby)

        if gs.hasBot:
            ms.selection_time_out_with_bot(ms.trty_set_time, len(gs.players), "set_cities")
        else:
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
            gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"Deploy your troops! {amount} deployable"}, room=player)
            gs.server.emit('troop_deployment', {'amount': amount}, room=player)

        if gs.hasBot:
            ms.selection_time_out_with_bot(ms.trty_set_time, len(gs.players), "initial_deploy")
        else:
            ms.selection_time_out(ms.trty_set_time, len(gs.players))

        gs.signal_view_clear()
        gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"Completed, waiting for others..."}, room=gs.lobby)
        gs.server.emit('change_click_event', {'event': None}, room=gs.lobby)
        gs.server.emit('troop_result', {'resp': True}, room=gs.lobby)
        gs.server.sleep(3)
        for player in gs.players:
            gs.clear_deployables(player)
    
    def start_skill_selection(self, gs, ms):
        gs.server.emit('set_new_announcement', {'async' : True, 'msg': "Choose your Ultimate War Art"}, room=gs.lobby)
        for player in gs.players:
            options = gs.SDIS.get_options(gs.complexity) if player != gs.Annihilator else gs.SDIS.get_Annihilator_options()
            if gs.players[player].isBot:
                gs.players[player].skill_options = gs.SDIS.get_bot_options(gs.complexity)
            gs.server.emit('choose_skill', {'options': options}, room=player)

        if gs.hasBot:
            ms.selection_time_out_with_bot(ms.trty_set_time, len(gs.players), "get_skill")
        else:
            ms.selection_time_out(ms.trty_set_time, len(gs.players))

        gs.signal_view_clear()

        for player in gs.players:
            # CM
            if not gs.players[player].skill:
                # Randomly assign mission to player
                gs.players[player].skill = gs.SDIS.initiate_skill(gs.SDIS.get_single_option(), player, gs) if player != gs.Annihilator else gs.SDIS.initiate_skill( gs.SDIS.get_Annihilator_options()[random.randint(0,7)], player, gs)