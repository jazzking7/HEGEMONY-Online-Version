from turn_loop_scheduler import *

EVENT_HANDLERS = {
    'R_D': ('reserve_deployment', False),
    'B_C': ('build_cities', True),
    'R_M': ('raise_megacities', True),
    'BFC': ('build_free_cities', False),
    'D_P': ('launch_orbital_strike', False),
    'A_S': ('paratrooper_attack', False),
    'C_T': ('corrupt_territory', False),
    'S_M': ('set_minefields', False),
    'B_S': ('build_silo', False),
    'LUS': ('launch_from_silo_inner', False),
    'M_R': ('make_ransom', False),
    'G_I': ('gather_intel', False),
    'S_F': ('set_forts', True),
    'S_H': ('set_hall', True),
    'L_N': ('logistic_nexus', True),
    'L_C': ('leyline_cross', True),
    'M_B': ('mobilization_bureau', True),
    'BFLC': ('build_free_leyline_crosses', False),
    'EP' : ('establish_pillars', False),
}

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
        # Event + Halter + ID
        self.concurrent_events = {}
        # Inter-turn skill effects
        self.interturn_events = []
        # Inter-turn connection event
        self.interturn_connections = {}
        # inner async
        self.stats_set = False # If stats of player already determined
        self.innerInterrupt = False
        # inter turn summit
        self.summit_requested = False
        self.summit_voter = {'y': 0, 'n': 0}
        self.global_peace_proposed = False
        # locking mechanism
        self.lock = threading.Lock()

        self.turn_token = 0

        # Main thread
        self.main_flow = threading.Thread(target=self.execute_game_events)

    def add_concurrent_event(self, event_name, pid):

        if event_name == 'LUS':
            def event_function():
                self.launch_from_silo(pid)
            event_thread = threading.Thread(target=event_function)
            self.concurrent_events[pid] = {
                'thread': event_thread,
                'flag': False
            }
            event_thread.start()
        elif event_name == 'D_P':
            def event_function():
                self.launch_divine_strike(pid)
            event_thread = threading.Thread(target=event_function)
            self.concurrent_events[pid] = {
                'thread': event_thread,
                'flag': False
            }
            event_thread.start()
        elif event_name == "M_R":
            def event_function():
                self.make_ransom_outturn(pid)
            event_thread = threading.Thread(target=event_function)
            self.concurrent_events[pid] = {
                'thread': event_thread,
                'flag': False
            }
            event_thread.start()


    def flush_concurrent_event(self, pid):
        if pid in self.concurrent_events:
            self.concurrent_events[pid]['flag'] = True
    
    def flush_all_concurrent_events(self):
        for pid in self.gs.players:
            self.flush_concurrent_event(pid)

    def selection_time_out(self, num_secs, count):
        self.selected = 0
        self.gs.server.emit('start_timeout',{'secs': num_secs}, room=self.gs.lobby)
        for _ in range(num_secs):
            if self.selected == count:
                break
            self.gs.server.sleep(1)
        self.gs.server.emit('stop_timeout', room=self.gs.lobby)

    # Timer for turn
    def activate_timer(self, num_secs, curr_player, token):
        sec = 0
        while (not self.terminated 
            and sec < num_secs 
            and not self.interrupt 
            and self.turn_token == token
            and self.gs.players[curr_player].connected):
            self.gs.server.sleep(1)  # non-blocking
            sec += 1
        if not self.interrupt and self.turn_token == token:
            self.terminated = True
        return

    def run_setup_events(self,):
        self.gs.server.sleep(15)
        self.gs.server.emit('set_up_announcement', {'msg': "Loading resources..."}, room=self.gs.lobby)
        self.gs.server.sleep(2)
        for event in self.SES:
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
        self.gs.server.emit('signal_show_btns', room=self.gs.lobby)
        self.run_turn_scheduler()

    # end game
    def halt_events(self,):
        self.lock.acquire()
        if not self.interrupt:
            self.interrupt = True
            curr = any(self.gs.players[p].connected for p in self.gs.players)
            if not curr:
                self.lock.release()
                print("Lobby Deleted")
                return
            self.gs.signal_view_clear()
            # PAUSE TO GIVE TIME TO COMPUTE END RESULT
            self.gs.server.sleep(2) 
            self.flush_all_concurrent_events()
            self.gs.game_over()
        self.lock.release()

    # INNER ASYNC EVENTS FROM HERE FORWARD
    def handle_async_event(self, data, pid):
        
        n = data['name']
        self.innerInterrupt = True  # Break current stage of the player's turn

        try:
            fn_name, needs_data = EVENT_HANDLERS[n]
        except KeyError:
            self.gs.server.emit('display_new_notification', {'msg': f'Unknown async event: {n}'}, room=pid)
            return

        handler = getattr(self, fn_name)

        self.gs.server.emit('signal_hide_btns', room=pid)

        if needs_data:
            handler(data, pid)
        else:
            handler(pid)

        self.gs.server.emit('signal_show_btns', room=pid)
        print(f"{self.gs.players[pid].name}'s async action thread completed.")
        self.innerInterrupt = False

        # resume loop event if not terminated | timer didn't stop
        if not self.terminated and not self.interrupt:
            self.gs.server.emit('signal_show_btns', room=pid)
            self.TLS.resume_loop(self, self.gs, pid, self.turn_token)
            print(f"{self.gs.players[pid].name}'s async action completed.")
        print("Exit async thread")

    def reserve_deployment(self, pid):

        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('change_click_event', {'event': "reserve_deployment"}, room=pid)
        self.gs.server.emit('reserve_deployment', {'amount': self.gs.players[pid].reserves}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].reserves == 0
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)
    
    def mobilization_bureau(self, data, pid):
        flist = []
        for t in self.gs.players[pid].territories:
            if not self.gs.map.territories[t].isCity and not self.gs.map.territories[t].isBureau and not self.gs.map.territories[t].isDeadZone and not self.gs.map.territories[t].isTransportcenter:
                flist.append(t)
        if len(flist) < int(data['amt']):
            self.gs.server.emit('display_new_notification', {'msg': 'Not enough territories to build the bureaus!'}, room=pid)
            return
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('set_bureau', {'amount': data['amt'], 'flist': flist}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "set_bureau"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].s_city_amt = int(data['amt']) # Borrowed from city building
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].s_city_amt == 0
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def leyline_cross(self, data, pid):
        flist = []
        for t in self.gs.players[pid].territories:
            if not self.gs.map.territories[t].isCapital and not self.gs.map.territories[t].isHall and not self.gs.map.territories[t].isDeadZone and not self.gs.map.territories[t].isLeyline:
                flist.append(t)
        if len(flist) < int(data['amt']):
            self.gs.server.emit('display_new_notification', {'msg': 'Not enough territories to build the leyline cross!'}, room=pid)
            return
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('set_leyline', {'amount': data['amt'], 'flist': flist}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "set_leyline"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].s_city_amt = int(data['amt']) # Borrowed from city building
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].s_city_amt == 0
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def logistic_nexus(self, data, pid):
        flist = []
        for t in self.gs.players[pid].territories:
            if not self.gs.map.territories[t].isCity and not self.gs.map.territories[t].isTransportcenter and not self.gs.map.territories[t].isDeadZone:
                flist.append(t)
        if len(flist) < int(data['amt']):
            self.gs.server.emit('display_new_notification', {'msg': 'Not enough territories to build the nexus!'}, room=pid)
            return
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('set_nexus', {'amount': data['amt'], 'flist': flist}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "set_nexus"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].s_city_amt = int(data['amt']) # Borrowed from city building
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].s_city_amt == 0
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)


    def set_hall(self, data, pid):
        flist = []
        for t in self.gs.players[pid].territories:
            if not self.gs.map.territories[t].isHall and not self.gs.map.territories[t].isCapital and not self.gs.map.territories[t].isDeadZone and not self.gs.map.territories[t].isLeyline:
                flist.append(t)
        if len(flist) < int(data['amt']):
            self.gs.server.emit('display_new_notification', {'msg': 'Not enough territories that can set hall of governance!'}, room=pid)
            return
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('set_hall', {'amount': data['amt'], 'flist': flist}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "set_hall"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].s_city_amt = int(data['amt']) # Borrowed from city building
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].s_city_amt == 0
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def set_forts(self, data, pid):
        flist = []
        for t in self.gs.players[pid].territories:
            if not self.gs.map.territories[t].isFort and not self.gs.map.territories[t].isDeadZone:
                flist.append(t)
        if len(flist) < int(data['amt']):
            self.gs.server.emit('display_new_notification', {'msg': 'Not enough territories that can be fortified!'}, room=pid)
            return
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('set_forts', {'amount': data['amt'], 'flist': flist}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "set_forts"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].s_city_amt = int(data['amt']) # Borrowed from city building
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].s_city_amt == 0
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def build_cities(self, data, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('build_cities', {'amount': data['amt']}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "build_cities"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].s_city_amt = int(data['amt'])
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].s_city_amt == 0
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def raise_megacities(self, data, pid):
        clist = []
        for t in self.gs.players[pid].territories:
            if self.gs.map.territories[t].isCity and not self.gs.in_secret_control(t, pid) and not self.gs.map.territories[t].isMegacity and not self.gs.map.territories[t].isTransportcenter:
                clist.append(t)
        if len(clist) < int(data['amt']):
            self.gs.server.emit('display_new_notification', {'msg': 'Not enough cities that can be upgraded to megacities!'}, room=pid)
            return
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('raise_megacities', {'amount': int(data['amt']), 'clist': clist}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "raise_megacities"}, room=pid)
        print(f"{self.gs.players[pid].name}'s async action started.")
        self.gs.players[pid].m_city_amt = int(data['amt'])
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].m_city_amt == 0
            self.gs.server.sleep(0.05)
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
        self.flush_all_concurrent_events()
        c = 0
        for player in self.gs.players:
            if self.gs.players[player].alive:
                c += 1
                self.gs.server.emit('summit_voting', {'msg': f"{self.gs.players[pid].name} has proposed a summit"}, room=player)
        self.gs.server.emit('signal_hide_btns', room=self.gs.lobby)
        self.selection_time_out(20, c)
        self.gs.server.emit('signal_show_btns', room=self.gs.lobby)
        if self.summit_voter['y'] > self.summit_voter['n']:
            self.gs.players[pid].num_summit -= 1
            self.activate_summit()
        else:
            self.gs.server.emit('summit_failed', {'msg': "VOTING FAILED, NO SUMMIT HELD!"}, room=self.gs.lobby)

    def launch_global_peace_procedures(self, player):
        pid = self.gs.pids[player]
        self.global_peace_proposed = False
        self.summit_voter = {'y': 0, 'n': 0}
        self.flush_all_concurrent_events()
        c = 0
        for player in self.gs.players:
            if self.gs.players[player].alive:
                c += 1
                self.gs.server.emit('summit_voting', {'msg': f"{self.gs.players[pid].name} has proposed a global peace. The game ends immediately if nobody refuse."}, room=player)
        self.gs.server.emit('signal_hide_btns', room=self.gs.lobby)
        self.selection_time_out(60, c)
        self.gs.server.emit('signal_show_btns', room=self.gs.lobby)
        if self.summit_voter['n']:
            self.gs.players[pid].num_global_cease -= 1
            self.gs.server.emit('summit_failed', {'msg': "VOTING FAILED, GLOBAL PEACE NOT ACHIEVED!"}, room=self.gs.lobby)
        else:
            self.flush_all_concurrent_events()
            self.gs.global_peace_game_over()
            self.gs.GES.interrupt = True

    def build_free_cities(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('build_free_cities', room=pid)
        self.gs.server.emit('change_click_event', {'event': "build_free_cities"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        self.gs.players[pid].skill.finish_building = False
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finish_building
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def build_free_leyline_crosses(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('build_free_leyline_crosses', room=pid)
        self.gs.server.emit('change_click_event', {'event': "build_free_leyline_crosses"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        self.gs.players[pid].skill.finish_building = False
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finish_building
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def establish_pillars(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        self.gs.server.emit('establish_pillars', room=pid)
        self.gs.server.emit('change_click_event', {'event': "establish_pillars"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        self.gs.players[pid].skill.finish_building = False
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finish_building
            self.gs.server.sleep(0.05)
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
            self.gs.server.sleep(0.05)
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
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def corrupt_territory(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        corruptables = [tid for tid in range(self.gs.map.num_nations) if tid not in self.gs.players[pid].territories and not self.gs.map.territories[tid].isMegacity]
        self.gs.players[pid].skill.finished_choosing = False
        self.gs.server.emit('corrupt_territory', {'targets': corruptables}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "corrupt_territory"}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finished_choosing
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def make_ransom(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        potential_targets = self.gs.players[pid].skill.get_potential_targets()
        self.gs.players[pid].skill.finished_choosing = False
        self.gs.server.emit('make_ransom', {'targets': potential_targets}, room=pid)
        self.gs.server.emit('change_click_event', {'event': None}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finished_choosing
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def gather_intel(self, pid):
        self.gs.server.emit('async_terminate_button_setup', room=pid)
        potential_targets = self.gs.players[pid].skill.get_potential_targets()
        self.gs.players[pid].skill.finished_choosing = False
        self.gs.server.emit('gather_intel', {'targets': potential_targets}, room=pid)
        self.gs.server.emit('change_click_event', {'event': None}, room=pid)
        print(f"{self.gs.players[pid].name}'s war art triggered an inner async event.")
        done = False
        while not done and self.innerInterrupt and not self.terminated and self.gs.players[pid].connected:
            done = self.gs.players[pid].skill.finished_choosing
            self.gs.server.sleep(0.05)
        print(f"{self.gs.players[pid].name}'s async action exited loop.")
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)

    def set_minefields(self, pid):
        player = self.gs.players[pid]
        if player.skill.active:
            if player.skill.max_minefields-len(player.skill.minefields) > 0:
                self.gs.server.emit('async_terminate_button_setup', room=pid)
                options = [tid for tid in player.territories if tid not in player.skill.minefields]
                player.skill.finished_setting = False

                self.gs.server.emit('set_minefields', {'targets': options, 'limits': player.skill.max_minefields-len(player.skill.minefields)}, room=pid)
                self.gs.server.emit('change_click_event', {'event': "set_minefields"}, room=pid)

                print(f"{player.name}'s war art triggered an inner async event.")
                done = False
                while not done and self.innerInterrupt and not self.terminated and player.connected:
                    done = player.skill.finished_setting
                    self.gs.server.sleep(0.05)
                print(f"{player.name}'s async action exited loop.")
                self.gs.server.emit("change_click_event", {'event': None}, room=pid)
                self.gs.server.emit("clear_view", room=pid)
            else:
                self.gs.server.emit("display_new_notification", {'msg': "Cannot set up more than 3 minefields!"}, room=pid)
    
    def build_silo(self, pid):
        player = self.gs.players[pid]
        if player.skill.active:
            if not player.skill.underground_silo:
                self.gs.server.emit('async_terminate_button_setup', room=pid)
                options = [tid for tid in player.territories]
                player.skill.finished_setting = False

                self.gs.server.emit('set_underground_silo', {'targets': options}, room=pid)
                self.gs.server.emit('change_click_event', {'event': "set_underground_silo"}, room=pid)

                print(f"{player.name}'s war art triggered an inner async event.")
                done = False
                while not done and self.innerInterrupt and not self.terminated and player.connected:
                    done = player.skill.finished_setting
                    self.gs.server.sleep(0.05)
                print(f"{player.name}'s async action exited loop.")
                self.gs.server.emit("change_click_event", {'event': None}, room=pid)
                self.gs.server.emit("clear_view", room=pid)
            else:
                self.gs.server.emit("display_new_notification", {'msg': "Cannot build more than 1 silo!"}, room=pid)

    # TBH switch from concurr to innerasync
    def launch_from_silo_inner(self, pid):
        player = self.gs.players[pid]
        skill = player.skill
        if skill.active:

            self.gs.server.emit('async_terminate_button_setup', room=pid)
            skill.finished_launching = False

            # options = self.gs.map.recursive_get_trty_with_depth(skill.underground_silo, [skill.underground_silo], 0, skill.range)
            options = self.gs.map.get_reachable_airspace(skill.underground_silo, skill.range)

            options = list(set(options) - set(player.territories))

            self.gs.server.emit('underground_silo_launch', {'targets': options, 'usages': skill.silo_usage - skill.silo_used}, room=pid)
            self.gs.server.emit('change_click_event', {'event': "underground_silo_launch"}, room=pid)

            print(f"{player.name}'s war art triggered an async event.")
            done = False
            while not done and self.innerInterrupt and not self.terminated and player.connected:
                done = skill.finished_launching
                self.gs.server.sleep(0.05)

            print(f"{player.name}'s async event exited loop.")
            self.gs.server.emit("change_click_event", {'event': None}, room=pid)
            self.gs.server.emit("clear_view", room=pid)
        else:
            self.gs.server.emit("display_new_notification", {'msg': "Launching operation has been sealed!"}, room=pid)

    # concurrent events 
    def launch_from_silo(self, pid):
        player = self.gs.players[pid]
        skill = player.skill
        if skill.active:

            self.gs.server.emit('concurr_terminate_event_setup', {'pid': pid}, room=pid)
            skill.finished_launching = False

            #options = self.gs.map.recursive_get_trty_with_depth(skill.underground_silo, [skill.underground_silo], 0, skill.range)
            options = self.gs.map.get_reachable_airspace(skill.underground_silo, skill.range)
            options = list(set(options) - set(player.territories))

            self.gs.server.emit('signal_hide_btns', room=pid)
            self.gs.server.emit('underground_silo_launch', {'targets': options, 'usages': skill.silo_usage - skill.silo_used}, room=pid)
            self.gs.server.emit('change_click_event', {'event': "underground_silo_launch"}, room=pid)

            print(f"{player.name}'s war art triggered a concurrent event.")
            done = self.concurrent_events[pid]['flag']
            while not skill.finished_launching and not done and player.connected:
                done = self.concurrent_events[pid]['flag']
                self.gs.server.sleep(0.05)
            del self.concurrent_events[pid]
            print(f"{player.name}'s concurrent event exited loop.")
            self.gs.server.emit('signal_show_btns', room=pid)
            self.gs.server.emit("clear_view", room=pid)
            # not the player's turn, clear click event
            if not (pid == self.gs.pids[self.current_player]):
                self.gs.server.emit("change_click_event", {'event': None}, room=pid)
            if skill.finished_launching:
                self.gs.server.emit("set_up_announcement", {'msg': "Missiles launched..."}, room=pid)
            else:
                self.gs.server.emit("set_up_announcement", {'msg': "Launching operation cancelled..."}, room=pid)
        else:
            self.gs.server.emit("display_new_notification", {'msg': "Launching operation has been sealed!"}, room=pid)
    
    def launch_divine_strike(self, pid):
        player = self.gs.players[pid]
        skill = player.skill
        if skill.active:

            self.gs.server.emit('concurr_terminate_event_setup', {'pid': pid}, room=pid)
            skill.finished_bombardment = False

            #options = self.gs.map.recursive_get_trty_with_depth(skill.underground_silo, [skill.underground_silo], 0, skill.range)
            strikables = [tid for tid in range(self.gs.map.num_nations) if tid not in self.gs.players[pid].territories]


            self.gs.server.emit('signal_hide_btns', room=pid)
            
            self.gs.server.emit('launch_orbital_strike_offturn', {'targets': strikables, 'usages': skill.limit-skill.offturn_used}, room=pid)
            self.gs.server.emit('change_click_event', {'event': "launch_orbital_strike_offturn"}, room=pid)

            print(f"{player.name}'s war art triggered a concurrent event.")
            done = self.concurrent_events[pid]['flag']
            while not skill.finished_bombardment and not done and player.connected:
                done = self.concurrent_events[pid]['flag']
                self.gs.server.sleep(0.05)
            del self.concurrent_events[pid]
            print(f"{player.name}'s concurrent event exited loop.")
            self.gs.server.emit('signal_show_btns', room=pid)
            self.gs.server.emit("clear_view", room=pid)
            # not the player's turn, clear click event
            if not (pid == self.gs.pids[self.current_player]):
                self.gs.server.emit("change_click_event", {'event': None}, room=pid)
            if skill.finished_bombardment:
                self.gs.server.emit("set_up_announcement", {'msg': "Orbital Strike launched..."}, room=pid)
            else:
                self.gs.server.emit("set_up_announcement", {'msg': "Launching operation cancelled..."}, room=pid)
        else:
            self.gs.server.emit("display_new_notification", {'msg': "Launching operation has been sealed!"}, room=pid)

    def make_ransom_outturn(self, pid):
        player = self.gs.players[pid]
        skill = player.skill
        if skill.active:

            self.gs.server.emit('concurr_terminate_event_setup', {'pid': pid}, room=pid)
            skill.finished_choosing = False

            potential_targets = self.gs.players[pid].skill.get_potential_targets()

            self.gs.server.emit('signal_hide_btns', room=pid)
            
            self.gs.server.emit('make_ransom', {'targets': potential_targets}, room=pid)
            self.gs.server.emit('change_click_event', {'event': None}, room=pid)

            print(f"{player.name}'s war art triggered a concurrent event.")
            done = self.concurrent_events[pid]['flag']
            while not skill.finished_choosing and not done and player.connected:
                done = self.concurrent_events[pid]['flag']
                self.gs.server.sleep(0.05)
            del self.concurrent_events[pid]
            print(f"{player.name}'s concurrent event exited loop.")
            self.gs.server.emit('signal_show_btns', room=pid)
            self.gs.server.emit("clear_view", room=pid)
            # not the player's turn, clear click event
            if not (pid == self.gs.pids[self.current_player]):
                self.gs.server.emit("change_click_event", {'event': None}, room=pid)
            if skill.finished_choosing:
                self.gs.server.emit("set_up_announcement", {'msg': "Ransomware activated..."}, room=pid)
            else:
                self.gs.server.emit("set_up_announcement", {'msg': "Ransomware cancelled..."}, room=pid)
        else:
            self.gs.server.emit("display_new_notification", {'msg': "Ransomeware has been sealed!"}, room=pid)