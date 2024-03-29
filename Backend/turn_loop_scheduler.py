from set_up_scheduler import *

class turn_loop_scheduler:

    # current_player -> index
    # curr_player refers to pid corresponding to the current_player

    def __init__(self, ):
        self.events = [
            Event("reinforcement", self.reinforcement),
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
                    done = atk_player.deployable_amt == 0
                if ms.terminated or ms.innerInterrupt:
                    return

            if event.name == 'conquer':
                # prevent immediate growth
                if not ms.stats_set:
                    atk_player.temp_stats = gs.get_player_battle_stats(atk_player)
                    ms.stats_set = True
                self.set_curr_state(ms, self.events[1])
                self.conquer(gs, pid)

                ms.stage_completed = False
                while not ms.stage_completed and not ms.innerInterrupt:
                    time.sleep(1)
                if ms.terminated or ms.innerInterrupt:
                    return
            if event.name == 'rearrangement':
                self.set_curr_state(ms, self.events[2])
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
        if gs.players[curr_p].deployable_amt == 0:
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

    def execute_turn_events(self, gs, ms, player):

        atk_player = gs.players[player]
        atk_player.turn_victory = False
        ms.stats_set = False

        self.set_curr_state(ms, self.events[0])
        self.reinforcement(gs, player)

        ms.stage_completed = False
        done = False
        while not ms.stage_completed and not done and not ms.innerInterrupt:
            done = atk_player.deployable_amt == 0
        if ms.terminated or ms.innerInterrupt:
            return

        # prevent immediate growth
        atk_player.temp_stats = gs.get_player_battle_stats(atk_player)
        ms.stats_set = True
        self.set_curr_state(ms, self.events[1])
        self.conquer(gs, player)

        ms.stage_completed = False
        while not ms.stage_completed and not ms.innerInterrupt:
            time.sleep(1)
        if ms.terminated or ms.innerInterrupt:
            return
        
        self.set_curr_state(ms, self.events[2])
        self.rearrange(gs, player)

        ms.stage_completed = False
        while not ms.stage_completed and not ms.innerInterrupt:
            time.sleep(1)
        if ms.terminated or ms.innerInterrupt:
            return
        
        # stop timer
        ms.terminated = True
        return
    
    def handle_end_turn(self, gs, player):
        # notify frontend to change event and clear controls
        gs.server.emit("change_click_event", {'event': None}, room=player)
        gs.server.emit("clear_view", room=player)
        gs.server.emit('signal_hide_btns', room=player)
        print(f"{gs.players[player].name}'s turn ends, buttons have been hidden.")
        # clear deployables
        gs.clear_deployables(player)
        # assign stars if applicable
        # CM
        p = gs.players[player]
        if p.turn_victory:
            p.stars += random.choices([1,2,3],[0.3, 0.4, 0.3],k=1)[0]
        print(f'{gs.players[player].name} special authority amount: {p.stars}')

    def execute_turn(self, gs, ms, curr_player):

        ms.curr_thread = threading.Thread(target=self.execute_turn_events, args=(gs, ms, curr_player))
        ms.timer = threading.Thread(target=ms.activate_timer, args=(60,))

        ms.terminated = False
        ms.curr_thread.start()

        gs.server.emit('start_timeout', {'secs': 60}, room=gs.lobby)
        print(f"{gs.players[curr_player].name}'s turn starts, buttons have been shown.")
        gs.server.emit('signal_show_btns', room=curr_player)
        
        ms.timer.start()
        ms.timer.join()
        gs.server.emit('stop_timeout', room=gs.lobby)

        ms.curr_thread.join()

        self.handle_end_turn(gs, curr_player)

    def run_turn_loop(self, gs, ms):
        curr_player = gs.pids[ms.current_player]
        while not ms.interrupt:
            if gs.players[curr_player].alive:
                self.execute_turn(gs, ms, curr_player)
            if ms.interrupt:
                return

            # inter_turn_summit
            if not ms.interrupt and ms.summit_requested:
                ms.launch_summit_procedures(ms.current_player)
             
            ms.current_player += 1
            if ms.current_player == len(gs.pids):
                ms.current_player = 0
                ms.round += 1
                # CM
                print(f"Round {ms.round} completed.")
            curr_player = gs.pids[ms.current_player]