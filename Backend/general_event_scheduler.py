from turn_loop_scheduler import *

class General_Event_Scheduler:

    def __init__(self, gs, setup_events):
        self.gs = gs
        self.SES = setup_events
        self.TLS = turn_loop_scheduler()

        # set up selection controller
        self.selected = 0
        # whole game interrupted
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
        # inner async
        self.stats_set = False
        self.innerInterrupt = False

    def selection_time_out(self, num_secs, count):
        self.selected = 0
        self.gs.server.emit('start_timeout',{'secs': num_secs}, room=self.gs.lobby)
        c = 0
        while self.selected != count and c < num_secs:
            time.sleep(1)
            c += 1
        self.gs.server.emit('stop_timeout', room=self.gs.lobby)

    def activate_timer(self, num_secs):
        sec = 0
        while not self.terminated and sec < num_secs and not self.interrupt:
            time.sleep(1)
            sec += 1
        self.stage_completed = True
        self.terminated = True
        return

    def run_setup_events(self,):
        time.sleep(3)
        for event in self.SES:
            event.executable(self.gs, self)
    
    def run_turn_scheduler(self,):
        self.TLS.run_turn_loop(self.gs, self)

    def execute_game_events(self,):
        self.run_setup_events()
        self.run_turn_scheduler()

    def halt_events(self,):
        self.interrupt = True

    # Inner async
    def handle_async_event(self, data, pid):
        
        n = data['name']
        self.innerInterrupt = True
  
        if n == 'F_A':
            self.curr_thread = threading.Thread(target=self.form_alliance, args=(data, pid))
        elif n == 'R_S':
            self.curr_thread = threading.Thread(target=self.request_summit, args=(data, pid))
        elif n == 'R_D':
            self.curr_thread = threading.Thread(target=self.reserve_deployment, args=(data, pid))
        elif n == 'U_I':
            self.curr_thread = threading.Thread(target=self.upgrade_infrastructure, args=(data, pid))
        elif n == 'B_C':
            self.curr_thread = threading.Thread(target=self.build_cities, args=(data, pid))
        
        self.curr_thread.start()
        self.curr_thread.join()
        self.innerInterrupt = False
        # resume loop event if not terminated
        if not self.terminated:
            self.TLS.resume_loop(self, self.gs, pid)

    def form_alliance(self, data, pid):
        return
    
    def request_summit(self, data, pid):
        return

    def reserve_deployment(self, data, pid):

        self.gs.server.emit('async_terminate', room=pid)
        self.gs.server.emit('change_click_event', {'event': "reserve_deployment"}, room=pid)
        self.gs.server.emit('reserve_deployment', {'amount': self.gs.players[pid].reserves}, room=pid)
        done = False
        while not done and self.innerInterrupt and not self.terminated:
            done = self.gs.players[pid].reserves == 0
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)


    def upgrade_infrastructure(self, data, pid):
        return

    def build_cities(self, data, pid):
        self.gs.server.emit('async_terminate', room=pid)
        self.gs.server.emit('build_cities', {'amount': data['amt']}, room=pid)
        self.gs.server.emit('change_click_event', {'event': "build_cities"}, room=pid)
        self.gs.players[pid].s_city_amt = data['amt']
        done = False
        while not done and self.innerInterrupt and not self.terminated:
            done = self.gs.players[pid].s_city_amt == 0
        self.gs.server.emit("change_click_event", {'event': None}, room=pid)
        self.gs.server.emit("clear_view", room=pid)