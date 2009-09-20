""" Harvest System Events"""

import time

__doc__ =  '''Harvest System Events - \xa9 wyleu 2008'''


from system_events import *
       
        
class SensorInit(Event):
    def __init__(self):
        self.name = "Sensor Init"

class SensorError(Event):
    def __init__(self, text):
        self.name = "Sensor ERROR %s" % text
        self.text = text

class SensorTypeDetect(Event):    # A sensor type detected by interface ...'
    def __init__(self, type):
        self.type = type
        self.name = 'Sensor type %s detected' % self.type

class SensorTypeConfirm(Event):     # A sensor type confirmed by database ...'
    def __init__(self, type):
        self.type = type
        self.name = 'Sensor type %s confirmed' % self.type

class SensorDetect(Event):               # A sensor  detected by interface ...'
    def __init__(self, address, type):
        self.address = address
        self.type = type
        self.name = 'Sensor %s detected' % self.address
        
class SensorConfirm(Event):          # A sensor confirmed by database ...'
    def __init__(self, address,type):
        self.address = address
        self.type = type
        self.name = 'Sensor  %s confirmed' % self.address

class SensorRead(Event):   # Read a specific sensor
    def __init__(self,address):
        self.address = address
        self.name = 'Sensor   %s read' % self.address

class SensorsRead(Event):    # Read all connected sensors
    def __init__(self):
        self.name = ' sensors read' 

class SensorValue(Event):     # Publish a Sensor Value
    def __init__(self,reading):
        self.reading = reading
        self.dowrite = True
        self.name = 'Sensor Reading %s ' % (self.reading)

class SensorsValue(Event):    # Publish all sensors value
    def __init__(self,dict):
        self.dict = dict
        self.dowrite = True
        self.name = '  %d Sensors read' % (len(self.dict))
