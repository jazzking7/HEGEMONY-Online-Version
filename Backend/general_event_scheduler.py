from turn_loop_scheduler import *

class General_Event_Scheduler:

    def __init__(self, gs, setup_events):
        self.gs = gs
        self.SES = setup_events
        self.TLS = turn_loop_scheduler()

        # set up selection controller
        self.selected = 0
        # loop interrupted
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
        while not self.terminated and sec < num_secs:
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