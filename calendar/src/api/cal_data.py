from generative_theming import GenerativeThemingModule
from datetime import datetime, timedelta
from tzlocal import get_localzone



class CalData:
    def __init__(self, canvas, id):
        """
            self.events is a dictionary where each key represents a month of the calendar and each value is 
            another dictionary mapping an event_id to an an event that occurs in month month 
        """
        #Maps months to their canvas elements
        self.months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 
                                      'September', 'October', 'November', 'December']

        self.canvases = {}
        self.themes = {}
        self.events = {}


        for ii in range(len(self.months)): 
            self.canvases[ii] = canvas
            prompt = "A day in " + self.months[ii] + ". The image you generate should NOT contain any text."
            self.themes[ii] = GenerativeThemingModule().generate_theme(prompt)
            self.events[ii] = {}

        self.id = id
    

    def generate_theme(self, month, affect=None):
        month_events = self.events[month]
        events = ', '.join([event.name for event in month_events.values()])
        month_name = self.months[month]
        themingModule = GenerativeThemingModule()
        new_prompt = themingModule.determine_prompt_from_affect(affect, month_name, events)
        self.themes[month] = themingModule.generate_theme(new_prompt)
        

    def add_event(self, month, coord1, coord2, event_id, event_name, event_start, event_end, assistant_scheduled=False):
        #assert(month>=0)
        #assert(month<11)
        new_event = Event(coord1, coord2, event_name, event_start, event_end, assistant_scheduled)
        month_events = self.events[month]
        month_events[event_id] = new_event


    def update_canvas(self, month, canvas):
        self.canvases[month] = canvas
    

    def delete_event(self, month, canvas, event_id): 
        #assert(month>=0)
        #assert(month<11)

        month_events = self.events[month]
        del month_events[event_id]
        self.canvases[month] = canvas
        events = ', '.join([event.name for event in month_events.values()])
        new_prompt = GenerativeThemingModule.generate_prompt(month, events)
        self.themes[month] = GenerativeThemingModule().generate_theme(new_prompt)


    def get_month_canvas(self, month): 
        #assert(month>=0)
        #assert(month<11)

        return self.canvases[month]


    def get_month_events(self, month): 
        #assert(month>=0)
        #assert(month<11)
        serializable_dict = {}
        for key, val in self.events[month].items(): 
            serializable_dict[key] = (val.coord1, val.coord2)
        return serializable_dict


    def get_events(self, months_from_today = 3):
        """
        Returns all events in the calendar scheduled within 
        months_from_today as a dictionary of lists mapping each event to a start and end time
        """
        events_dict = {"events": []}
        today = datetime.now(get_localzone())
        # Simplifying assumption that each month has ~30 days
        end = today + timedelta(days=30*months_from_today) 

        current_month = today.month - 1
        for month in range(current_month, current_month + months_from_today):
            for event_id, event in self.events[month].items():
                if today <= datetime.fromisoformat(event.event_end) and datetime.fromisoformat(event.event_start) >= end:
                    events_dict["events"].append({"event": {"start": event.event_start, "end": event.event_end}})
        return events_dict


    def get_month_theme(self, month): 
        return self.themes[month]


    def get_cal_id(self):
        return self.id
    
    
class Event: 
    def __init__(self, coord1, coord2, name, event_start, event_end, assistant_scheduled=False):
        self.coord1 = coord1
        self.coord2 = coord2
        self.name = name
        self.assistant_scheduled=assistant_scheduled
        self.event_start = event_start
        self.event_end = event_end