class Event_Scheduler:

    def __init__(self, ):
        self.events = [self.event1, self.event2, self.event3]
    
    def event1(self,):
        print("Event1 done")
    
    def event2(self,):
        print("Event2 done")

    def event3(self,):
        print("Event3 done")
    
    def execute(self,):
        for event in self.events:
            event()

class Event:
    def __init__(self, name, event):
        self.name = name
        self.event = event
        self.event_duration = 30
    
    
    def distribute_missions():
        lobby = lobbies[ players[request.sid]['lobby_id'] ]
        if request.sid not in lobby['waitlist']:
            lobby['waitlist'].append(request.sid)
            print(request.sid, " ready to play")
        if len(lobby['waitlist']) == len(lobby['players']):
            print("Mission Sent")
            for player in lobby['waitlist']:
                continents = ['Pannotia', 'Zealandia', 'Baltica', 'Rodinia', 'Kenorland', 'Kalahari']
                socketio.emit('get_mission', {'msg': f'Mission: capture {random.choice(continents)}'}, room=player)
            lobby['waitlist'] = []

    def start_color_distribution():
        lobby = lobbies[ players[request.sid]['lobby_id'] ]
        if request.sid not in lobby['waitlist']:
            lobby['waitlist'].append(request.sid)
            print(request.sid, " ready to choose")
        if len(lobby['waitlist']) == len(lobby['players']):
            time.sleep(10)
            with open('Setting_Options/colorOptions.json') as file:
                color_options = json.load(file)
            for player in lobby['waitlist']:
                socketio.emit('choose_color', {'msg': 'Choose a color to represent your country', 'options': color_options}, room=player)
            lobby['waitlist'] = []
    
    def start_territorial_distribution():
        return
    
    def start_capital_settlement():
        return
    
    def start_city_settlement():
        return
    
    def start_initial_deployment():
        return
    
    def start_skill_choosing():
        return
    

e = Event_Scheduler()
e.execute()
a = Event("Actions", e.execute)
a.event()