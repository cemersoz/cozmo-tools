"""
  Events and the Event Router

  This file implements an event router scheme modeled after the
  one in Tekkotsu.

"""

def set_robot(_robot):
    global robot
    robot = _robot

def get_robot():
    if robot:
        return robot
    else:
        raise Exception("Don't have a robot.")

global erouter

class Event:
    """Base class for all events."""
    def __init__(self):
        self.source = None


class CompletionEvent(Event):
    """Signals completion of a state node's action."""
    def __init__(self,source):
        super().__init__()
        self.source = source


class DataEvent(Event):
    """Signals a data item broadcase by the node."""
    def __init__(self,value):
        super().__init__()
        self.source = value

class TapEvent(Event):
    """Signals detection of a tap on a light cube."""
    def __init__(self,cube,intensity,duration):
        super().__init__()
        self.source = cube
        self.intensity = intensity
        self.duration = duration


################

class EventRouter:
    """An event router drives the state machine."""
    def __init__(self):
        self.dispatch_table = dict(
               {
                CompletionEvent : dict() ,
        TapEvent : dict()
               }
            )

    def start(self):
        pass
        ### TODO: add a handler for cube tap API events

    def stop(self):
        pass
        ### TODO: remove all handlers for API events

    def add_listener(self, listener, event_type, source):
        if not issubclass(event_type, Event):
            raise TypeError('% is not an Event' % event_type)
        source_dict = self.dispatch_table.get(event_type, dict())
        handlers = source_dict.get(source, [])
        handlers.append(listener.handle_event)
        source_dict[source] = handlers
        self.dispatch_table[event_type] = source_dict

    def remove_listener(self, listener, event_type, source):
        if not issubclass(event_type, Event):
            raise TypeError('% is not an Event' % event_type)
        source_dict = self.dispatch_table.get(event_type, None)
        if source_dict is None: return
        handlers = source_dict.get(source, None)
        if handlers is None: return
        try:
            handlers.remove(listener.handle_event)
        except: pass

    def _get_listeners(self,event):
        source_dict = self.dispatch_table.get(type(event), None)
        if source_dict is None:  # no listeners for this event type
            return []
        matches = source_dict.get(event.source, [])
        wildcards = source_dict.get(None, [])
        if not wildcards:
            return matches
        else:  # append specific listeners and wildcard listeners
            matches = matches.copy()
            matches.append(wildcards)
            return matches

    def post(self,event):
        if not isinstance(event,Event):
            raise TypeError('%s is not an Event' % event)
        for listener in self._get_listeners(event):
            #print('scheduling',listener,'on',event)
            get_robot().loop.call_soon(listener,event)

erouter = EventRouter()

################

class EventListener:
    """Parent class for both StateNode and Transition."""
    def __init__(self):
        self.running = False
        self.name = None
        self.polling_interval = None
        self.poll_handle = None

    def set_name(self,name):
        self.name = name

    def start(self):
        self.running = True
        if polling_interval:
            self.next_poll()
        print(self,'running')

    def stop(self):
        self.running = False
        if self.poll_handle: poll_handle.cancel()
        print(self,'stopped')

    def handle_event(self, event):
        if not self.running:
            print('Handler',self,'not running, but received',event)
        else:
            pass

    def set_polling_interval(self,interval):
        if isinstance(interval, (int,float)):
            self.polling_interval = interval
        else:
            raise TypeError('interval must be a number')

    def next_poll(self):
        """Call this to schedule the next polling interval."""
        self.poll_handle = \
            get_robot().loop.call_later(self.polling_interval, self.poll)

    def poll(self):
        """Dummy polling function in case sublass neglects to supply one."""
        print('%s has no poll() method' % self)