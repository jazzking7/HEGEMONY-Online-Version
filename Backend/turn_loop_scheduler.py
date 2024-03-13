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

    def execute_turn_events(self, gs, ms, player):

        atk_player = gs.players[player]
        atk_player.turn_victory = False

        self.set_curr_state(ms, self.events[0])
        self.reinforcement(gs, player)
        ms.stage_completed = False
        done = False
        while not ms.stage_completed and not done:
            done = atk_player.deployable_amt == 0
        if ms.terminated:
            return

        self.set_curr_state(ms, self.events[1])
        # Prevent Immediate Stats growth
        atk_player.temp_stats = gs.get_player_battle_stats(atk_player)
        self.conquer(gs, player)
        ms.stage_completed = False
        while not ms.stage_completed:
            time.sleep(1)
        if ms.terminated:
            return
        
        self.set_curr_state(ms, self.events[2])
        self.rearrange(gs, player)
        ms.stage_completed = False
        while not ms.stage_completed:
            time.sleep(1)
        if ms.terminated:
            return
        # stop timer
        ms.terminated = True
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

    def execute_turn(self, gs, ms, curr_player):

        ms.curr_thread = threading.Thread(target=self.execute_turn_events, args=(gs, ms, curr_player))
        ms.timer = threading.Thread(target=ms.activate_timer, args=(30,))

        ms.terminated = False
        ms.curr_thread.start()

        gs.server.emit('start_timeout',{'secs': 30}, room=gs.lobby)
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
            ms.current_player += 1
            if ms.current_player == len(gs.pids):
                ms.current_player = 0
                ms.round += 1
                print(f"Round {ms.round} completed.")
            curr_player = gs.pids[ms.current_player]