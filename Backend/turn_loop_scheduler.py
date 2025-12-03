from set_up_scheduler import *

class turn_loop_scheduler:

    # current_player -> index
    # curr_player refers to pid corresponding to the current_player

    def __init__(self, ):
        self.events = [
            Event("reinforcement", self.reinforcement),
            Event("preparation", self.preparation),
            Event("conquer", self.conquer),
            Event("rearrangement", self.rearrange)
        ]

    def set_curr_state(self, ms, event):
        ms.current_event = event
        return

    def resume_loop(self, ms, gs, pid, token):
        # Guard: only the active turn + active player may re-arm
        if token != ms.turn_token:
            return
        if ms.terminated or ms.interrupt or ms.current_event is None:
            return
        if pid != gs.pids[ms.current_player]:
            return

        ev = ms.current_event.name

        # IMPORTANT: do NOT call set_curr_state here, do NOT iterate remaining events.
        # Just re-emit the CURRENT stage's UI so the client sees controls again.
        if ev == 'reinforcement':
            self.reinforcement(gs, pid)   # emits troop_deployment + click event
        elif ev == 'preparation':
            self.preparation(gs, pid)     # emits preparation + clears click event
        elif ev == 'conquer':
            self.conquer(gs, pid)         # emits conquest + click event 'conquest'
        elif ev == 'rearrangement':
            self.rearrange(gs, pid)       # emits rearrangement + click event 'rearrange'

        return


    def reinforcement(self, gs, curr_p):
        for player in gs.pids:
            if player != curr_p:
                gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"{gs.players[curr_p].name}'s turn: reinforcement"}, room=player)
        gs.server.emit('change_click_event', {'event': "troop_deployment"}, room=curr_p)
        print(f"Player has {gs.players[curr_p].deployable_amt} deployable amount")
        if gs.players[curr_p].deployable_amt < 1: #???
            d_amt = gs.get_deployable_amt(curr_p)
            # Robinhood activated    
            for p in gs.players:
                if gs.players[p].skill:
                    if gs.players[p].skill.name == 'Robinhood':
                        if curr_p in gs.players[p].skill.targets:
                            d_amt = gs.players[p].skill.leech_off_reinforcements(d_amt)
            # Zealous Expansion Reserve Booster
            # Air superiority
            if gs.players[curr_p].skill:
                if gs.players[curr_p].skill.active and gs.players[curr_p].skill.name == "Zealous_Expansion":
                    gs.players[curr_p].reserves += gs.players[curr_p].skill.bonus_level * 5
                    gs.update_private_status(curr_p)
                    gs.server.emit('show_notification_right', {
                                'message': f'+{gs.players[curr_p].skill.bonus_level * 5} Reserves',
                                'duration': 3000,
                                "text_color": "#1E40AF", "bg_color": "#BFDBFE"
                            }, room=curr_p)
                if gs.players[curr_p].skill.active and gs.players[curr_p].skill.name == "Air_Superiority":
                    gs.players[curr_p].skill.long_arm_jurisdiction()
                if gs.players[curr_p].skill.active and gs.players[curr_p].skill.name == "Babylon":
                    if 8 in gs.players[curr_p].skill.passives:
                        gs.players[curr_p].skill.long_arm_jurisdiction()

            # Fanatic receive troop booster
            for miss in gs.Mset:
                if miss.player == curr_p:
                    if miss.name == 'Fanatic':
                        for t in miss.targets:
                            if t in gs.players[curr_p].territories:
                                gs.players[curr_p].reserves += 1
                                gs.server.emit('show_notification_right', {
                                    'message': f'+1 Reserves',
                                    'duration': 3000,
                                    "text_color": "#1E40AF", "bg_color": "#BFDBFE"
                                }, room=curr_p)
                        gs.update_private_status(curr_p)
                        break
            gs.players[curr_p].deployable_amt = d_amt
            print(f"Player has {gs.players[curr_p].deployable_amt} deployable amount")
        gs.server.emit('set_new_announcement', {'async' : False, 'curr_phase' : 'DEPLOY', 'msg': f" | {gs.players[curr_p].deployable_amt} DEPLOYABLE"}, room=curr_p)
        gs.server.emit("troop_deployment", {'amount': gs.players[curr_p].deployable_amt}, room=curr_p)
        return

    def preparation(self, gs, curr_player):
        for player in gs.players:
            if player != curr_player:
                gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"{gs.players[curr_player].name}'s turn: preparation"}, room=player)
        gs.server.emit('set_new_announcement', {'async' : False, 'curr_phase' : 'PREPARE', 'msg': f""}, room=curr_player)
        gs.server.emit("change_click_event", {'event': None}, room=curr_player)
        gs.server.emit("preparation", room=curr_player)
        return

    def conquer(self, gs, curr_player):
        for player in gs.players:
            if player != curr_player:
                gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"{gs.players[curr_player].name}'s turn: conquest"}, room=player)
        gs.server.emit('set_new_announcement', {'async' : False, 'curr_phase' : 'ATTACK', 'msg': f""}, room=curr_player)
        gs.server.emit("change_click_event", {'event': 'conquest'}, room=curr_player)
        gs.server.emit("conquest", room=curr_player)
        return
    
    def rearrange(self, gs, curr_player):
        for player in gs.players:
            if player != curr_player:
                gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"{gs.players[curr_player].name}'s turn: rearrangement"}, room=player)
        gs.server.emit('set_new_announcement', {'async' : False, 'curr_phase' : 'REARRANGE', 'msg': f""}, room=curr_player)
        gs.server.emit("change_click_event", {'event': 'rearrange'}, room=curr_player)
        gs.server.emit("rearrangement", room=curr_player)
        return

    def execute_turn_events(self, gs, ms, player, token):
        ms.flush_concurrent_event(player)
        # Player executing the turn
        atk_player = gs.players[player]
        atk_player.deployable_amt = 0
        # Reset turn based victory
        atk_player.turn_victory = False
        atk_player.con_amt = 0
        # Iron wall turn off if there is any
        if atk_player.skill:
            if atk_player.skill.name == "Iron_Wall" and atk_player.skill.ironwall:
                atk_player.skill.turn_off_iron_wall()
            if atk_player.skill.active:
                if atk_player.skill.name == "Mass Mobilization":
                    atk_player.reserves += round((atk_player.total_troops * 15)/100)
                    gs.server.emit('show_notification_right', {
                                    'message': f'+{round((atk_player.total_troops * 15)/100)} Reserves',
                                    'duration': 3000,
                                    "text_color": "#1E40AF", "bg_color": "#BFDBFE"
                                }, room=player)
                if atk_player.skill.name == "Babylon":
                    if 1 in atk_player.skill.passives:
                        atk_player.reserves += round((atk_player.total_troops * 10)/100)
                        gs.server.emit('show_notification_right', {
                                    'message': f'+{round((atk_player.total_troops * 10)/100)} Reserves',
                                    'duration': 3000,
                                    "text_color": "#1E40AF", "bg_color": "#BFDBFE"
                                }, room=player)

        # Hall giving authority
        # Bureau recruitement
        numBureaux = 0
        for t in atk_player.territories:
            if gs.map.territories[t].isBureau:
                numBureaux += 1
            if gs.map.territories[t].isHall:
                atk_player.stars += 1
                self.gs.server.emit('show_notification_right', {
                                'message': f'+ 1☆',
                                'duration': 3000,
                                "text_color": "#B45309", "bg_color": "#FDE68A"
                            }, room=player)
        
        atk_player.reserves += round((atk_player.total_troops * numBureaux * 15)/100)
        if round((atk_player.total_troops * numBureaux * 15)/100):
            gs.server.emit('show_notification_right', {
                                        'message': f'+{round((atk_player.total_troops * numBureaux * 15)/100)} Reserves',
                                        'duration': 3000,
                                        "text_color": "#1E40AF", "bg_color": "#BFDBFE"
                                    }, room=player)
        gs.update_private_status(player)

        # Player temporary battle stats not updated
        ms.stats_set = False
        ms.stage_completed = False
        self.set_curr_state(ms, self.events[0])
        self.reinforcement(gs, player)

        ms.stage_completed = False
        
        done = False
        while (not ms.stage_completed
            and not ms.terminated
            and atk_player.connected
            and token == ms.turn_token):
            if ms.innerInterrupt:
                gs.server.sleep(0.05)  # park during inner async
                continue
            # your “auto-finish” condition:
            done = atk_player.deployable_amt < 1
            if done:
                ms.stage_completed = True
                break
            gs.server.sleep(0.05)
        if ms.terminated or not atk_player.connected or token != ms.turn_token:
            return

        ms.stage_completed = False
        self.set_curr_state(ms, self.events[1])
        self.preparation(gs, player)

        while (not ms.stage_completed
            and not ms.terminated
            and atk_player.connected
            and token == ms.turn_token):
            if ms.innerInterrupt:
                gs.server.sleep(0.05)
                continue
            gs.server.sleep(1)
        if ms.terminated or not atk_player.connected or token != ms.turn_token:
            return

        # prevent immediate growth
        atk_player.temp_stats = gs.get_player_battle_stats(atk_player)
        ms.stats_set = True
        ms.stage_completed = False
        self.set_curr_state(ms, self.events[2])
        self.conquer(gs, player)

        while (not ms.stage_completed
            and not ms.terminated
            and atk_player.connected
            and token == ms.turn_token):
            if ms.innerInterrupt:
                gs.server.sleep(0.05)
                continue
            gs.server.sleep(1)
        if ms.terminated or not atk_player.connected or token != ms.turn_token:
            if ms.terminated and atk_player.skill and atk_player.skill.name == "Necromancer":
                atk_player.skill.soul_harvest()
            return
        
        ms.stage_completed = False
        self.set_curr_state(ms, self.events[3])
        self.rearrange(gs, player)

        # (Necromancer soul harvest after rearrange if you had it)
        if atk_player.skill and atk_player.skill.name == "Necromancer":
            atk_player.skill.soul_harvest()

        while (not ms.stage_completed
            and not ms.terminated
            and atk_player.connected
            and token == ms.turn_token):
            if ms.innerInterrupt:
                gs.server.sleep(0.05)
                continue
            gs.server.sleep(1)
        if ms.terminated or not atk_player.connected or token != ms.turn_token:
            return
        
        # stop timer
        ms.terminated = True
        return
    
    def handle_end_turn(self, ms, gs, player):
        if not ms.interrupt:
            # notify frontend to change event and clear controls
            gs.server.emit("change_click_event", {'event': None}, room=player)
            gs.server.emit("clear_view", room=player)
            gs.server.emit('clear_otherHighlight', room=gs.lobby)
            print(f"{gs.players[player].name}'s turn ended.")
            # clear deployables
            gs.clear_deployables(player)
            # assign stars if applicable
            # CM
            p = gs.players[player]
            # Get stars probability based on territory conquered
            if p.turn_victory or gs.peaceFirst:
                bonus = max(min(gs.get_player_infra_level(p),9),0)
                infraticks = [3,3,2,2,1,1,1,1,1]
                ticks = sum(infraticks[:bonus])
                cap = min(0.03*ticks, 0.45)
                print(f"4 star cap: {cap*100}%")
                     
                advance = False
                for trty in p.territories:
                    if gs.map.territories[trty].isTransportcenter:
                        advance = True
                        break

                max_con = 9
                con_amt = min(p.con_amt, max_con)

                if gs.peaceFirst:
                    eff_con = max_con - con_amt
                else:
                    eff_con = con_amt

                s_amt = 0
                if not advance:
                    s1, s2, s3, s4 = 0.45, 0.3, 0.25, 0.0
                    per4 = cap / 9.0 if cap > 0 else 0.0
                    for _ in range(eff_con):
                        d = min(0.05, s1)
                        s1 -= d
                        add4 = min(per4, cap - s4, d)
                        s4 += add4
                        rem = d - add4
                        s2 += rem * 0.5
                        s3 += rem * 0.5
                    s1 = max(0, s1)
                    s_amt = random.choices([1,2,3,4],[s1, s2, s3, s4],k=1)[0]
                else:
                    s1, s2, s3, s4 = 0.45, 0.3, 0.25, 0
                    per4 = cap / 6.0 if cap > 0 else 0.0
                    for i in range(eff_con):
                        if i < 6:
                            d = min(0.075, s1)
                            s1 -= d
                            add4 = min(per4, cap - s4, d)
                            s4 += add4
                            rem = d - add4
                            s2 += rem * 0.5
                            s3 += rem * 0.5
                        else:
                            s2 -= 0.1
                            s3 += 0.05
                            s4 += 0.05
                    s1 = max(0, s1)
                    s_amt = random.choices([1,2,3,4],[s1,s2,s3,s4],k=1)[0]

                # Ice Age!
                if gs.in_ice_age:
                    if p.skill:
                        if p.skill.name != 'Realm_of_Permafrost':
                            s_amt = 0
                        else:
                            if not p.skill.active:
                                s_amt = 0
                    else:
                        s_amt = 0

                # Robinhood!
                for pid in gs.players:
                    if gs.players[pid].skill:
                        if gs.players[pid].skill.name == "Robinhood":
                            if player in gs.players[pid].skill.targets:
                                s_amt = gs.players[pid].skill.leech_off_stars(s_amt)

                p.stars += s_amt
                if s_amt:
                    gs.server.emit('show_notification_right', {
                                'message': f'+ {s_amt}☆',
                                'duration': 3000,
                                "text_color": "#B45309", "bg_color": "#FDE68A"
                            }, room=player)

                moreBlessings = False
                if p.skill:
                    if p.skill.active and p.skill.name == "Archmage":
                        moreBlessings = True
                leyprob = p.numLeylines * 14 if moreBlessings else p.numLeylines * 11
                if not moreBlessings:
                    leyprob = min(leyprob, 66)
                else:
                    leyprob = min(leyprob, 84)

                if random.randint(1, 100) <= leyprob:
                    print("Leyline Bonus Received.")
                    if random.randint(1, 100) > 40:
                        ramt = p.numLeylines * 5 if moreBlessings else p.numLeylines * 4
                        p.reserves += ramt
                        gs.server.emit('show_notification_right', {
                            'message': f'+{ramt} Reserves',
                            'duration': 3000,
                            "text_color": "#000000", "bg_color": "#6987D5"
                        }, room=player)
                    else:
                        samt = p.numLeylines + 1 if moreBlessings else p.numLeylines
                        p.stars += samt
                        gs.server.emit('show_notification_right', {
                            'message': f'+ {samt}☆',
                            'duration': 3000,
                            "text_color": "#000000", "bg_color": "#6987D5"
                        }, room=player)
                    gs.server.emit("playSFX", {"sfx": "blessing"}, room=player)
                    gs.server.emit('show_notification_center', {
                        'message': 'YOU HAVE RECEIVED LEYLINE BLESSINGS',
                        'duration': 3000,
                        "text_color": "#000000", "bg_color": "#6987D5"
                    }, room=player)
                    gs.server.sleep(1)

            if gs.copro:
                for miss in gs.Mset:
                    if miss.player == player:
                        if miss.name in ['Guardian', 'Populist', 'Expansionist', 'Dominator', 'Industrialist',
                                            'Fanatic', 'Polarizer', 'Unifier']:
                            gs.players[player].stars += 1
                            gs.server.emit('show_notification_right', {
                                'message': '+ 1☆',
                                'duration': 3000,
                                "text_color": "#B45309", "bg_color": "#FDE68A"
                            }, room=player)
                            break

            # Dictator receives more stars
            # Ares clear stats boost
            # Zealous and Industrial clear restrictions
            if p.skill:
                if p.skill.hasTurnEffect:
                    p.skill.apply_turn_effect()

            # Update private overview
            gs.update_private_status(player)
            print(f'{gs.players[player].name} special authority amount: {p.stars}')
            print(f'{gs.players[player].name} reserve amount: {p.reserves}')

    def execute_turn(self, gs, ms, curr_player):
        # gs -> game states    ms -> master scheduler/gs.GES
        ms.turn_token += 1
        token = ms.turn_token

        ms.terminated = False
        ms.stage_completed = False
        ms.innerInterrupt = False

        gs.server.start_background_task(self.execute_turn_events, gs, ms, curr_player, token)
        gs.server.start_background_task(ms.activate_timer, ms.turn_time, curr_player, token)
        
        gs.server.emit('start_timeout', {'secs': ms.turn_time}, room=gs.lobby)
        gs.server.emit('set_countdown', room=curr_player)
        print(f"{gs.players[curr_player].name}'s turn started.")
        print(f"Their pid is {curr_player}")
        gs.server.emit('signal_show_btns', room=curr_player)
        gs.server.emit('signal_turn_start', room=curr_player)

        while not ms.terminated and not ms.interrupt and token == ms.turn_token:
            gs.server.sleep(0.1)

        gs.server.emit('stop_timeout', room=gs.lobby)
        
        # Handle end of turn
        self.handle_end_turn(ms, gs, curr_player)


    # MAIN LOOP FOR TURN BASED EVENTS
    def run_turn_loop(self, gs, ms):

        # current_player = index of player in the queue
        curr_player = gs.pids[ms.current_player]

        while not ms.interrupt:

            if ms.round == 0:
                gs.players[curr_player].stars += 0 if (ms.current_player <= 2) else math.floor(ms.current_player / 2)
                gs.update_private_status(curr_player)
                gs.server.emit('show_notification_right', {
                                'message': f'+ {math.floor(ms.current_player / 2)}☆',
                                'duration': 3000,
                                "text_color": "#B45309", "bg_color": "#FDE68A"
                            }, room=curr_player)

            # checking if player is alive | permitting entry
            if gs.players[curr_player].alive:
                self.execute_turn(gs, ms, curr_player)
            if ms.interrupt:
                return
            
            # inter_turn_skill_effect
            if ms.interturn_events: 
                for event in ms.interturn_events:
                    event.execute_interturn()
                ms.interturn_events = []

            # inter_turn connection event
            if ms.interturn_connections:
                for pid in ms.interturn_connections:
                    gs.server.emit('set_new_announcement', {'async' : True, 'msg': f"{gs.players[pid].name} is reconnecting..."}, room=gs.lobby)
                    c = 0
                    while not ms.interturn_connections[pid] and not ms.interrupt and c <= 60:
                        gs.server.sleep(1)
                        c += 1
                    gs.update_all_views(pid)
                ms.interturn_connections = {}

            # inter_turn_summit
            if not ms.interrupt and ms.summit_requested:
                ms.launch_summit_procedures(ms.current_player)

            # global peace
            if not ms.interrupt and ms.global_peace_proposed:
                ms.launch_global_peace_procedures(ms.current_player)
                if ms.interrupt:
                    return

            # next player 
            ms.current_player += 1

            # next round
            if ms.current_player == len(gs.pids):
                ms.current_player = 0
                ms.round += 1
                # CM
                gs.signal_MTrackers('round')
                gs.update_global_status()

                # update cooldown
                for p in gs.players:
                    if gs.players[p].skill:
                        if gs.players[p].skill.hasRoundEffect:
                            gs.players[p].skill.apply_round_effect()

                # set ice age
                turnIceOn = False
                if gs.set_ice_age:
                    gs.set_ice_age = False
                    if gs.in_ice_age:
                        gs.in_ice_age += 2
                    else:
                        turnIceOn = True
                        gs.in_ice_age += 3
                # update ice age
                if gs.in_ice_age:
                    gs.in_ice_age -= 1
                    if gs.in_ice_age:
                        if turnIceOn:
                            gs.server.emit('ice_age_on', {}, room=gs.lobby)
                        gs.server.emit('show_notification_center', {
                                'message': f'ICE AGE ONGOING, NUMBER OF ROUNDS LEFT: {gs.in_ice_age}',
                                'duration': 5000,
                                "text_color": "#FAFEFF", "bg_color": "#3F7EB3"
                            }, room=gs.lobby)
                    else:
                        gs.server.emit('show_notification_center', {
                                'message': f'ICE AGE TERMINATED',
                                'duration': 5000,
                                "text_color": "#FAFEFF", "bg_color": "#3F7EB3"
                            }, room=gs.lobby)
                        gs.server.emit('ice_age_off', {}, room=gs.lobby)
                 # nuclear deadzone kill troops
                for index, t in enumerate(gs.map.territories):
                    if t.isDeadZone:
                        losses = math.ceil(t.troops/5)
                        t.troops -= losses
                        for ps in gs.players:
                            if index in gs.players[ps].territories:
                                gs.players[ps].total_troops -= losses

                                # Ares' Blessing Rage Meter check
                                if gs.players[ps].skill:
                                    if gs.players[ps].skill.name == "Ares' Blessing" and gs.players[ps].skill.active:
                                        gs.players[ps].skill.checking_rage_meter()
                                gs.update_LAO(ps)
                                gs.update_player_stats()
                                gs.get_SUP()
                                gs.update_global_status()
                                gs.signal_MTrackers('popu')
                                break
                        gs.server.emit('update_trty_display', {index: {'troops': t.troops}}, room=gs.lobby)
                        gs.server.emit('battle_casualties', {
                            f'{index}': {'tid': index, 'number': losses},
                        }, room=gs.lobby)
                        t.isDeadZone -= 1
                        if not t.isDeadZone:
                            gs.server.emit('update_trty_display', {index: {'hasEffect': 'gone'}}, room=gs.lobby)

                # Dangerous Mission announcement
                for miss in gs.Mset:
                    if miss.name == "Loyalist":
                        if ms.round == 3:
                            gs.server.emit('playSFX', {"sfx": "alarm"}, room=gs.lobby)
                            gs.server.emit('show_notification_center', {
                                'message': 'PRESENCE OF LOYALISTS DETECTED! PROCEED WITH CAUTION!',
                                'duration': 5000,
                                "text_color": "#D9534F", "bg_color": "#F0AD4E"
                            }, room=gs.lobby)
                            gs.server.sleep(5)
                    if miss.name == "Annihilator":
                        if ms.round == 2:
                            gs.server.emit('playSFX', {"sfx": "alarm"}, room=gs.lobby)
                            gs.server.emit('show_notification_center', {
                                'message': 'PRESENCE OF ANNIHILATOR DETECTED! HIGH RISK SITUATION!',
                                'duration': 5000,
                                "text_color": "#D9534F", "bg_color": "#F0AD4E"
                            }, room=gs.lobby)
                            gs.server.sleep(5)
                    if miss.name == "Survivalist":
                        if ms.round == 5:
                            gs.server.emit('playSFX', {"sfx": "alarm"}, room=gs.lobby)
                            gs.server.emit('show_notification_center', {
                                'message': 'PRESENCE OF SURVIVALIST DETECTED! PROCEED WITH CAUTION!',
                                'duration': 5000,
                                "text_color": "#D9534F", "bg_color": "#F0AD4E"
                            }, room=gs.lobby)
                            gs.server.sleep(5)
                
                if gs.doctrineOn and gs.applied_doctrine:
                    gs.server.emit('show_notification_center', {
                                'message': 'Doctrine is deactivated',
                                'duration': 3000,
                                "text_color": "#000000", "bg_color": "#6987D5"
                            }, room=gs.lobby)
                    gs.server.sleep(3)
                    gs.applied_doctrine = None
                    gs.peaceFirst = False
                    gs.inflation = False
                    gs.anarchy = False
                    gs.turtle = False
                    gs.embargo = False
                    gs.suspension = False
                    gs.copro = False

                if (ms.round-1) % 2 == 0 and gs.doctrineOn:
                    ms.choose_doctrine(gs.SUP)

                print(f"Round {ms.round-1} completed.")
            curr_player = gs.pids[ms.current_player]