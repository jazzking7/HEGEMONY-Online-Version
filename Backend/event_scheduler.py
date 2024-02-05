class Event:
    def __init__(self, name, event):
        self.name = name
        self.event_function = event

    def execute(self,):
        self.event_function()

class Event_Scheduler:

    def __init__(self, ):
        self.events = [Event('1', Event_Scheduler.event1), Event('2', Event_Scheduler.event2), Event('3', Event_Scheduler.event3)]
    
    @staticmethod
    def event1():
        print("Event1 done")
    
    @staticmethod
    def event2():
        print("Event2 done")

    @staticmethod
    def event3():
        print("Event3 done")
    
    def execute_events(self,):
        for event in self.events:
            event.execute()

e = Event_Scheduler()
e.execute_events()