""" Harvest System Events"""

import time

__doc__ =  '''Harvest System Events - \xa9 wyleu 2008'''

class Event:
    """ This is the superclass fro events"""
    def __init__(self):
        self.name ='Generic Event'

    def __repr__(self):
        return self.name

class TickEvent(Event):
    def __init__(self, ticktime = None):
        self.name = "CPU Tick Event"
        if ticktime:
            self.time = ticktime
        else:
            self.time = time.time()
    def __repr__(self):
        return '%s: %s' %(self.name, time.ctime(self.time))
        

class QuitEvent(Event):
    def __init__(self):
        self.name = "Quit Event"

class StartEvent(Event):
    def __init__(self):
        self.name = "Start Event"

class IdentEvent(Event):
    def __init__(self, name = 'Ident'):
        self.name = 'Ident %s' % name


class TickerStartEvent(Event):
    def __init__(self, duration):
        self.name = "Ticker Start Event"
        self.duration = duration

class TickerStopEvent(Event):
    def __init__(self):
        self.name = "Ticker Stop Event"

class ErrorEvent(Event):
    def __init__(self, err ='Error Text'):
        self.name = "Error Event "
        self.err  = err
