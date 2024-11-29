from turn_loop_scheduler import *

class General_Event_Scheduler:

    def __init__(self, gs, setup_events, time_settings):
        self.gs = gs
        self.SES = setup_events
        self.TLS = turn_loop_scheduler()
        self.trty_set_time = time_settings[0]
        self.power_set_time = time_settings[1]
        self.turn_time = time_settings[2]

        # set up selection controller
        self.selected = 0
        # WHOLE GAME INTERRUPT
        self.interrupt = False
        # current turn terminated
        self.terminated = False
        # current stage of a turn terminated
        self.stage_completed = False
        # current round
        self.round = 0
        # thread for turn execution -> serves the player who is on their turn
        self.curr_thread = None
        # thread for timer
        self.timer = None
        # current event for keeping track of turn stages
        self.current_event = None
        self.current_player = 0
        # stack of events in case of interruption
        self.event_stack = []
        # inner async
        self.stats_set = False # If stats of player already determined
        self.innerInterrupt = False
        # inter turn summit
        self.summit_requested = False
        self.summit_voter = {'y': 0, 'n': 0}
        self.global_peace_proposed = False
        # locking mechanism
        self.lock = threading.Lock()

        # Main thread
        self.main_flow = threading.Thread(target=self.execute_game_events)

    def selection_time_out(self, num_secs, count):
        self.selected = 0
        self.gs.server.emit('start_timeout',{'secs': num_secs}, room=self.gs.lobby)
        c = 0
        while self.selected != count and c < num_secs:
            time.sleep(1)
            c += 1
        self.gs.server.emit('stop_timeout', room=self.gs.lobby)

    # Timer for turn
    def activate_timer(self, num_secs, curr_player):
        sec = 0
        while not self.terminated and sec < num_secs and not self.interrupt and self.gs.players[curr_player].connected:
            time.sleep(1)
            sec += 1
        self.stage_completed = True
        self.terminated = True
        return

    def run_setup_events(self,):
        time.sleep(6)
        self.gs.server.emit('set_up_announcement', {'msg': "Loading resources..."}, room=self.gs.lobby)
        time.sleep(2)
        for event in self.SES:
            print("Event Executed", event)
            event.executable(self.gs, self)
            if self.interrupt:
                return
    
    def run_turn_scheduler(self,):
        self.TLS.run_turn_loop(self.gs, self)

    def execute_game_events(self,):
        print("Flow Started")
        self.run_setup_events()
        if self.interrupt:
            return
        self.gs.send_player_list()
        self.gs.get_LAO()
        self.gs.get_MTO()
        self.gs.get_HIP()
        self.gs.get_TIP()
        self.gs.get_SUP()
        self.gs.update_global_status()
        if self.interrupt:
            return
        for mk in self.gs.MTrackers:
            if mk != 'round':
                self.gs.MTrackers[mk].event.set()
        if self.interrupt:
            return
        self.run_turn_scheduler()

    # end game
    def halt_events(self,):
        self.lock.acquire()
        if not self.interrupt:
            self.interrupt = True
            self.gs.signal_view_clear()
            # PAUSE TO GIVE TIME TO COMPUTE END RESULT
            time.sleep(2)
            self.gs.game_over()
        self.lock.release()

    # INNER ASYNC EVENTS FROM HERE FORWARD
    def handle_async_event(self, data, pid):
        
        n = data['name']
        self.innerInterrupt = True  # Break current stage of the player's turn

        # Change current thread to handle the async event
        if n == 'R_D':
            self.curr_thread = threading.Thread(target=self.reserve_deployment, args=(pid,))
        elif n == 'B_C':
            self.curr_thread = threading.Thread(target=self.build_cities, args=(data, pid))
        elif n == 'BFC':
            self.curr_thread = threading.Thread(target=self.build_free_cities, args=(pid,))
        elif n == 'D_P':
            self.curr_thread = threading.Thread(target=self.launch_orbital_strike, args=(pid,))
        elif n == 'A_S':
            self.curr_thread = threading.Thread(target=self.paratrooper_attack, args=(pid,))
        elif n == 'C_T':
            self.curr_thread = threading.Thread(target=self.corrupt_territory, args=(pid,))
        
        self.curr_thread.start()
        self.curr_thread.join()
        print(f"{self.gs.players[pid].name}'s async action thread completed.")
        self.innerInterrupt = False

        # resume loop event if not terminated | timer didn't stop
        if not self.terminated:
            self.gs.server.emit('signal_show_btns', room=pid)
            print(f"{self.gs.players[pid].name}'s async action completed.")
            self.curr_thread = threading.Thread(target=self.TLS.resume_loop, args=(self, self.gs, pid))
            self.curr_thread.start()
        print("Exit async thread")

    def reserve_deployment(self, pid):

        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('change_click_event', {'event': "reserve_deployment"}, room=pid)
        self.gs.server.emit('reserve_deployment', {'amount': self.gs.players[pid].reserves}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].reserves == 0
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def build_cities(self, data, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('build_cities', {'amount': data['amt']}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "build_cities"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].s_city_amt = data['amt']
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].s_city_amt == 0
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def activate_summit(self,):
        self.gs.server.emit('activate_summit', room=self.gs.lobby)
        self.selection_time_out(60, len(self.gs.players))

    def launch_summit_procedures(self, player):
        pid = self.gs.pids[player]
        self.summit_voter = {'y': 0, 'n': 0}
        self.summit_requested = False
        
        c = 0
        for player in self.gs.players:
            if self.gs.players[player].alive:
                c += 1
                self.gs.server.emit('summit_voting', {'msg': f"{self.gs.players[pid].name} has proposed a summit"}, room=player)

        self.selection_time_out(20, c)
        if self.summit_voter['y'] > self.summit_voter['n']:
            self.gs.players[pid].num_summit -= 1
            self.activate_summit()
        else:
            self.gs.server.emit('summit_failed', {'msg': "VOTING FAILED, NO SUMMIT HELD!"}, room=self.gs.lobby)

    def launch_global_peace_procedures(self, player):
        pid = self.gs.pids[player]
        self.global_peace_proposed = False
        self.summit_voter = {'y': 0, 'n': 0}

        c = 0
        for player in self.gs.players:
            if self.gs.players[player].alive:
                c += 1
                self.gs.server.emit('summit_voting', {'msg': f"{self.gs.players[pid].name} has proposed a global peace. The game ends immediately if nobody refuse."}, room=player)

        self.selection_time_out(60, c)
        if self.summit_voter['n']:
            self.gs.players[pid].num_global_cease -= 1
            self.gs.server.emit('summit_failed', {'msg': "VOTING FAILED, GLOBAL PEACE NOT ACHIEVED!"}, room=self.gs.lobby)
        else:
            self.gs.global_peace_game_over()
            self.gs.GES.interrupt = True

    def update_all_views_for_reconnected_player(self, pid):
        
        New_thread = threading.Thread(target=self.gs.update_all_views, args=(pid, ))
        New_thread.start()

    def build_free_cities(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('build_free_cities', room=pid)
        self.gs.server.emit('change_click_event', {'event': "build_free_cities"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        self.gs.players[pid].skill.finish_building = False
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finish_building
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def launch_orbital_strike(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)

        strikables = [tid for tid in range(self.gs.map.num_nations) if tid not in self.gs.players[pid].territories]

        self.gs.server.emit('launch_orbital_strike', {'targets': strikables}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "launch_orbital_strike"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        self.gs.players[pid].skill.finished_bombardment = False
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finished_bombardment
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def paratrooper_attack(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('paratrooper_attack', room=pid)
        self.gs.server.emit('change_click_event', {'event': "paratrooper_attack"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.limit == 0
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def corrupt_territory(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        corruptables = [tid for tid in range(self.gs.map.num_nations) if tid not in self.gs.players[pid].territories]
        self.gs.players[pid].skill.finised_choosing = False
        self.gs.server.emit('corrupt_territory', {'targets': corruptables}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "corrupt_territory"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finised_choosing
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)