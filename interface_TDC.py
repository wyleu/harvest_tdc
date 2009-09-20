"""interface_TDC.py"""


__doc__ =  '''Harvest interface_TDC - \xa9 wyleu 2008,2009

'''

import os
import datetime
import Queue
import threading
import asyncore
import socket

from event_manager import *
from system_events import *
from sensor_events import *

from tdc.tdcproxy_sender import tdcproxy_sender
from tdc.tdcproxy_server import tdcproxy_server


class Interface_TDC(object):
    def __init__(self, evManager):

        self.evManager = evManager
        self.evManager.RegisterListener( self )
        self.paradict = None
        self.sensorlist = []
        
        self.inqueue = Queue.Queue()
        self.running = True
        self.thread1 = threading.Thread(target =self.workerThread1)
        self.thread1.start()


    def Notify(self, event):
        if isinstance(event, StartEvent):
            self.allTypeBroadcast()
            self.allIDBroadcast()
            self.running = True
            self.evManager.Post(IdentEvent('interface_TDC'))


        elif isinstance(event, QuitEvent):
            self.endApplication()


        elif isinstance(event, TickEvent):
            self.processIncoming()

        elif isinstance(event, SensorsRead):
            pass

        elif isinstance(event, SensorTypeConfirm):   
            self.typedict[event.type] = True

        elif isinstance(event, SensorConfirm):    
            self.iddict[event.type] = True
            

    def workerThread1(self):
        try:
            tdcpsend = tdcproxy_sender()
            print ' Got the sender up'
        except socket.error, fred:
            event =SensorError(fred)
            self.evManager.Post(event)
            raise socket.error


            
        #try:
        tdcpserv = tdcproxy_server(host = '192.168.0.50', port = 10001, queue = self.inqueue, sender = tdcpsend)
        #except socket.error, fred:
        #    event =SensorError(fred)
        #    self.evManager.Post(event)
        #    raise socket.error

        # assert(False)
        
        """ This is where we do asynchronous things"""
        while self.running:
            asyncore.loop(timeout= 1, count = 5)

        print 'TDC Async core cleanly shutdown'


    def processIncoming(self):
        """ Handle all the messages in the queue"""
        while self.inqueue.qsize():
            try:
                msg = self.inqueue.get(0)
                # Check the contents and do stuff with it
                print 'Somthing Down the Queue', msg
                # self.l.config(text = msg)

            except Queue.Empty:
                # Shouldn't really happen
                pass

    def endApplication(self):
        print 'Killing the TDC thread'
        self.running = False
        

    def allTypeBroadcast(self):    # Broadcast the connected types
        l = self.allTypeExtract()
        for item in l:
            ev = SensorTypeDetect(item)
            self.evManager.Post(ev)

    def allTypeExtract(self):    # Extract the connected sensor types
        self.typedict = {}
        self.typedict['TDC4'] = False
        return self.typedict.keys()


    def allIDExtract(self):            # Get a dict of sensors
        self.iddict = {}                # The sensor dictionary
        for item in self.sensorlist:
            self.iddict[item.id] = item

        return self.iddict
    
    def allIDBroadcast(self):      # Broadcast dict of sensors
        l = self.allIDExtract()
        for item in l:
            ev = SensorDetect(item, l[item].type)
            self.evManager.Post(ev)
            self.getSensorValue(item)

        
if __name__ == '__main__':
    evm = EventManager()
    spinner = CPUSpinnerController(evm)
    itdc = Interface_TDC(evm)

    spinner.Run()

    
                
    
