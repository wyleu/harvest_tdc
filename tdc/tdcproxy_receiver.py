"""tdcproxy_receiver.py"""

import asynchat
import asyncore
import tdc
import socket

from tdcproxy_sender import *



class tdcproxy_receiver(asynchat.async_chat):

    channel_counter = 0
    
    def __init__(self, server ,(conn, addr)):
        asynchat.async_chat.__init__(self, conn)
        self.in_payload = False
        self.server = server
        self.id = tdcproxy_receiver.channel_counter
        tdcproxy_receiver.channel_counter = tdcproxy_receiver.channel_counter + 1
        self.set_terminator(tdc.size_header_data)                                                                              # pull in the Sorel header
        if self.server.sender:                                                                                               # there is a sender set up and waiting
            self.sender = self.server.sender
        else:
            self.sender = tdcproxy_sender(self, server.there)                                            # Make up a tdcproxy_sender
            self.server.sender = self.sender
        self.sender.id = self.id
        self.packet = None
        self.buffer = ''
        self.total = 0
        self.opened = True
        
    def handle_connect(self):
        pass


    def collect_incoming_data(self, data):
        try:
            self.total = self.total + len(data)
            # if self.server.queue:
                # rep = 'tdcproxy_receiver:-cc:-%d bytes:-%d' % ( self.channel_counter, self.total)
                # self.server.report('r%d' % self.id, rep)
                
                #self.server.queue.put(rep)
            # print ' tdcproxy_receiver Collecting'
            self.buffer = self.buffer + data
        except:
            print ' Ive just fallen over'


    def found_terminator(self):
        # print' Found a receiver terminator'
        data = self.buffer
        self.buffer = ''
        
        if self.in_payload:
            self.in_payload = False  # kill the payload flag
            self.packet.process(data)
            #print 'A packet:-', self.packet
            self.set_terminator(1)
            # print 'Receiver Packet sending on', self.packet.getpacket()
            
            self.server.report('s%d' % self.id ,'  %s :- %s' % ( self.packet.protocol, self.packet.command ) )  
            self.sender.push(self.packet.getpacket())


        else:
            # print 'Receiver data:',
            if data=='\x47':   # First byte of magic byte
                #print 'First receiver magic'
                self.set_terminator(tdc.size_header_data -1)   # pull in the Sorel header
                return
            elif  len(data) == (tdc.size_header_data -1):
                if data[0] !='\xAA':
                    self.set_terminator(1)
                    return
                try:
                    self.packet = tdc.tdcpacket('\x47' + data)
                     
                except:
                    print 'unrecognized receiver Header'
                    self.set_terminator(1)
                else:
                    self.in_payload = True
                    #print 'Found a Magic'
                    #print 'Size of payload:-', self.packet.size_payload
                    self.set_terminator(self.packet.size_payload)
            else:
                self.set_terminator(1)
                return   # chew up non magic bytes

            
        # print '==>()  %s'   % (repr(data))

    def handle_close(self):
        print 'GOT A CLOSE!!'
        self.opened = False
        self.close()
