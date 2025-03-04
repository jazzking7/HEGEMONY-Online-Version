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

    def resume_loop(self, ms, gs, pid):
        curr_event = ms.current_event
        c = 0
        for i, event in enumerate(self.events):
            if event == curr_event:
                c = i
                break
        atk_player = gs.players[pid]
        for event in self.events[c:]:
            if event.name == 'reinforcement':
                self.set_curr_state(ms, self.events[0])
                self.reinforcement(gs, pid)
                ms.stage_completed = False
                done = False
                while not ms.stage_completed and not done and not ms.innerInterrupt:
                    done = atk_player.deployable_amt < 1
                if ms.terminated or ms.innerInterrupt:
                    return
                
            if event.name == 'preparation':
                self.set_curr_state(ms, self.events[1])
                self.preparation(gs, pid)

                ms.stage_completed = False
                while not ms.stage_completed and not ms.innerInterrupt and atk_player.connected:
                    time.sleep(1)
                if ms.terminated or ms.innerInterrupt or not atk_player.connected:
                    return

            if event.name == 'conquer':
                # prevent immediate growth
                if not ms.stats_set:
                    atk_player.temp_stats = gs.get_player_battle_stats(atk_player)
                    ms.stats_set = True
                self.set_curr_state(ms, self.events[2])
                self.conquer(gs, pid)

                ms.stage_completed = False
                while not ms.stage_completed and not ms.innerInterrupt:
                    time.sleep(1)
                if ms.terminated or ms.innerInterrupt:
                    return
            if event.name == 'rearrangement':
                self.set_curr_state(ms, self.events[3])
                self.rearrange(gs, pid)

                ms.stage_completed = False
                while not ms.stage_completed and not ms.innerInterrupt:
                    time.sleep(1)
                if ms.terminated or ms.innerInterrupt:
                    return
        # stop timer
        ms.terminated = True
        return

    def reinforcement(self, gs, curr_p):
        for player in gs.pids:
            if player != curr_p:
                gs.server.emit('set_up_announcement', {'msg': f"{gs.players[curr_p].name}'s turn: reinforcement"}, room=player)
        gs.server.emit('change_click_event', {'event': "troop_deployment"}, room=curr_p)
        print(f"Player has {gs.players[curr_p].deployable_amt} deployable amount")
        if gs.players[curr_p].deployable_amt < 1: #???
            d_amt = gs.get_deployable_amt(curr_p)
            # Robinhood activated    
            for p in gs.players:
                if gs.players[p].skill:
                    if gs.players[p].skill.name == 'Robinhood':
                        if curr_p in gs.players[p].skill.targets and curr_p != p:
                            d_amt = gs.players[p].skill.leech_off_reinforcements(d_amt)
            # Zealous Expansion Reserve Booster
            # Air superiority
            if gs.players[curr_p].skill:
                if gs.players[curr_p].skill.active and gs.players[curr_p].skill.name == "Zealous_Expansion":
                    gs.players[curr_p].reserves += gs.players[curr_p].infrastructure_upgrade
                    gs.update_private_status(curr_p)
                if gs.players[curr_p].skill.active and gs.players[curr_p].skill.name == "Air_Superiority":
                    gs.players[curr_p].skill.long_arm_jurisdiction()

            # Fanatic receive troop booster
            for miss in gs.Mset:
                if miss.player == curr_p:
                    if miss.name == 'Fanatic':
                        for t in miss.targets:
                            if t in gs.players[curr_p].territories:
                                gs.players[curr_p].reserves += 1
                        gs.update_private_status(curr_p)
                        break
            gs.players[curr_p].deployable_amt = d_amt
            print(f"Player has {gs.players[curr_p].deployable_amt} deployable amount")
        gs.server.emit("troop_deployment", {'amount': gs.players[curr_p].deployable_amt}, room=curr_p)
        return

    def preparation(self, gs, curr_player):
        gs.server.emit('set_up_announcement', {'msg': f"{gs.players[curr_player].name}'s turn: preparation"}, room=gs.lobby)
        gs.server.emit("change_click_event", {'event': None}, room=curr_player)
        gs.server.emit("preparation", room=curr_player)
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

    def execute_turn_events(self, gs, ms, player):
        ms.flush_concurrent_event(player)
        # Player executing the turn
        atk_player = gs.players[player]
        # Reset turn based victory
        atk_player.turn_victory = False
        atk_player.con_amt = 0
        # Player temporary battle stats not updated
        ms.stats_set = False

        self.set_curr_state(ms, self.events[0])
        self.reinforcement(gs, player)

        ms.stage_completed = False
        done = False
        while not ms.stage_completed and not done and not ms.innerInterrupt and atk_player.connected:
            done = atk_player.deployable_amt < 1
        if ms.terminated or ms.innerInterrupt or not atk_player.connected:
            return

        self.set_curr_state(ms, self.events[1])
        self.preparation(gs, player)

        ms.stage_completed = False
        while not ms.stage_completed and not ms.innerInterrupt and atk_player.connected:
            time.sleep(1)
        if ms.terminated or ms.innerInterrupt or not atk_player.connected:
            return

        # prevent immediate growth
        atk_player.temp_stats = gs.get_player_battle_stats(atk_player)
        # Set stats_set to True to prevent innerAsync actions from giving battle stats growth
        ms.stats_set = True
        self.set_curr_state(ms, self.events[2])
        self.conquer(gs, player)

        ms.stage_completed = False
        while not ms.stage_completed and not ms.innerInterrupt and atk_player.connected:
            time.sleep(1)
        if ms.terminated or ms.innerInterrupt or not atk_player.connected:
            return
        
        self.set_curr_state(ms, self.events[3])
        self.rearrange(gs, player)

        ms.stage_completed = False
        while not ms.stage_completed and not ms.innerInterrupt and atk_player.connected:
            time.sleep(1)
        if ms.terminated or ms.innerInterrupt or not atk_player.connected:
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
            if p.turn_victory:
                s1, s2, s3 = 0.45, 0.3, 0.25
                p.con_amt = 9 if p.con_amt > 9 else p.con_amt
                for _ in range(p.con_amt):
                    s1 -= 0.05
                    s2 += 0.025
                    s3 += 0.025

                s_amt = random.choices([1,2,3],[s1, s2, s3],k=1)[0]

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
                            if player in gs.players[pid].skill.targets and player != pid:
                                s_amt = gs.players[pid].skill.leech_off_stars(s_amt)

                p.stars += s_amt

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

        # Thread for turn
        ms.curr_thread = threading.Thread(target=self.execute_turn_events, args=(gs, ms, curr_player))
        # Timer for turn
        ms.timer = threading.Thread(target=ms.activate_timer, args=(ms.turn_time, curr_player))

        ms.terminated = False
        ms.curr_thread.start()

        gs.server.emit('start_timeout', {'secs': ms.turn_time}, room=gs.lobby)
        print(f"{gs.players[curr_player].name}'s turn started.")
        gs.server.emit('signal_show_btns', room=curr_player)
        gs.server.emit('signal_turn_start', room=curr_player)

        # Timer and curr_thread both depends on self.terminate for counting or executing event
        # When one of them terminates, the other also terminates
        ms.timer.start()
        ms.timer.join()
        gs.server.emit('stop_timeout', room=gs.lobby)
        ms.curr_thread.join()
        
        # Handle end of turn
        self.handle_end_turn(ms, gs, curr_player)


    # MAIN LOOP FOR TURN BASED EVENTS
    def run_turn_loop(self, gs, ms):

        # current_player = index of player in the queue
        curr_player = gs.pids[ms.current_player]

        while not ms.interrupt:

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
                if gs.round_based_win:
                    ms.halt_events()
                # update cooldown
                for p in gs.players:
                    if gs.players[p].skill:
                        if gs.players[p].skill.hasRoundEffect:
                            gs.players[p].skill.apply_round_effect()

                # set ice age
                if gs.set_ice_age:
                    gs.set_ice_age = False
                    gs.in_ice_age += 3
                # update ice age
                if gs.in_ice_age:
                    gs.in_ice_age -= 1
                    if gs.in_ice_age:
                        gs.server.emit("display_special_notification", {"msg": f"ICE AGE ONGOING, NUMBER OF ROUNDS LEFT: {gs.in_ice_age}", "t_color": "#FAFEFF", "b_color": "#3F7EB3"}, room=gs.lobby)
                    else:
                        gs.server.emit("display_special_notification", {"msg": "ICE AGE TERMINATED", "t_color": "#FAFEFF", "b_color": "#3F7EB3"}, room=gs.lobby)
                # nuclear deadzone kill troops
                for index, t in enumerate(gs.map.territories):
                    if t.isDeadZone:
                        losses = math.ceil(t.troops/2.5)
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

                # Loyalist announcement
                for miss in gs.Mset:
                    if miss.name == "Loyalist":
                        if ms.round == 2:
                            time.sleep(2)
                            gs.server.emit("display_special_notification", {"msg": f"PRESENCE OF LOYALISTS DETECTED, PROCEED WITH CAUTION.", "t_color": "#D9534F", "b_color": "#F0AD4E"}, room=gs.lobby)
                print(f"Round {ms.round} completed.")
            curr_player = gs.pids[ms.current_player]