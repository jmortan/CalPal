from generative_theming import GenerativeThemingModule

class CalData:
    def __init__(self, canvas, months, id):
        #Maps months to their canvas elements
        self.months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 
                                      'September', 'October', 'November', 'December']
        theming = GenerativeThemingModule()

        self.canvases = {}
        self.themes = {}
        self.events = {}

        for ii in range(len(self.months)): 
            self.canvases[ii] = canvas
            prompt = "A day in " + self.months[ii] + " in the style of a painting"
            self.themes[ii] = theming.generate_theme(prompt)
            self.events[ii] = {}

        self.id = id

    def generate_prompt(self, month_events, month):
        events = ', '.join([event.name for event in month_events.values()])
        new_prompt = "A day in " + self.months[month] + " with " + events + "in the style of a painting"
        return new_prompt
        
    def add_event(self, month, canvas, coord1, coord2, event_id, event_name):
        #assert(month>=0)
        #assert(month<11)
        new_event = Event(coord1, coord2, event_name)
        month_events = self.events[month]
        month_events[event_id] = new_event
        self.canvases[month] = canvas

        new_prompt = self.generate_prompt(month_events, month)
        self.themes[month] = GenerativeThemingModule().generate_theme(new_prompt)


    def delete_event(self, month, canvas, event_id): 
        #assert(month>=0)
        #assert(month<11)

        month_events = self.events[month]
        del month_events[event_id]
        self.canvases[month] = canvas

        new_prompt = self.generate_prompt(month_events, month)
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

    def get_month_theme(self, month): 
        return self.themes[month]

    def get_cal_id(self):
        return self.id
    
    
class Event: 
    def __init__(self, coord1, coord2, name):
        self.coord1 = coord1
        self.coord2 = coord2
        self.name = name