""" Harvest System Events"""


__doc__ =  '''Harvest Event Manager - \xa9 wyleu 2008'''




from system_events import *
from tools import *
import time


class EventManager(object):
    """ This object is reponsible for co-ordinating most communication between the Model, View and CONTROLLERS."""
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue = []

    def RegisterListener(self, listener):
        """ Stick one on the list"""
        self.listeners [listener] = 1

    def UnregisterListener(self, listener):
        """ knock one off the list"""
        if listener in self.listeners .keys():
            del self.listeners [listener]

    def Post(self, event):
        if not isinstance(event, TickEvent):    # Don't Display Tick Events
            pp( event, 'An Event:')

        for listener in self.listeners.keys():
            # Note weakrefs tidy themselves up
            # Tell them to do stuff
            listener.Notify ( event )

class CPUSpinnerController:
    def __init__(self, evManager):
        self.evManager= evManager
        self.evManager.RegisterListener(self)

        self.keepGoing = True

    def Run(self):
        #print 'CPU Spinner Starting...'
        event =StartEvent()
        self.evManager.Post(event)
        event =IdentEvent('CPU Spinner')
        self.evManager.Post(event)
        try:
            while self.keepGoing:
                time.sleep(1)
                event =TickEvent()
                self.evManager.Post(event)
        except KeyboardInterrupt:
            print 'Going to try to quit ...'
            event =QuitEvent()
            self.evManager.Post(event)
            
        #print 'CPU Spinner stopped'

    def Notify(self, event):
        if isinstance(event, QuitEvent):
            # This will stop the while loop
            print 'Stopping CPU Spinner in 5 seconds'
            time.sleep(5)
            self.keepGoing = False

if __name__ == '__main__':
    print 'running tests...'
    evm = EventManager()
    spinner = CPUSpinnerController(evm)


    class testrunner(object):
        def __init__(self, evManager):
            self.evManager = evManager
            self.evManager.RegisterListener( self )
            
        def Notify(self, event):
            if isinstance( event, TickEvent):   # Show everything including ticks...
                # Draw Everything
                pp (event)

            if isinstance(event, QuitEvent):
                sys.exit()
    tr = testrunner(evm)
    
    spinner.Run()

