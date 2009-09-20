"""tdcproxy_sender.py"""

import asynchat
import asyncore
import tdc
import socket
import time


class mock_server(object):
    def __init__(self):
        self.receiver = None
    def report (self, no, text):
        print 'No:=%s Text:=%s' % (no, text)

class mock_receiver(object):
    def __init__(self,server):
        self.server = server
        self.opened = True

    def push(self,data):
        print 'Pushed %d data bytes' % len(data)
        

ms = mock_server()
mr = mock_receiver(ms)


class tdcproxy_sender(asynchat.async_chat):

    channel_counter = 0
    
    def __init__(self, receiver = mr , address = ('192.168.0.50',10001)):
        
        asynchat.async_chat.__init__(self)
        self.receiver = receiver
        self.server = self.receiver.server
        self.id = tdcproxy_sender.channel_counter
        tdcproxy_sender.channel_counter = tdcproxy_sender.channel_counter + 1
        self.in_payload = False
        self.set_terminator(None)   
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = ''
        self.packet = None
        self.set_terminator(1)
        self.connect(address)
        self.total = 0
        
    def handle_connect(self):
        pass
        # print 'tdcproxy_sender has been presented with something:-'
        # print 'Terminator:-', self.get_terminator()

    def collect_incoming_data(self, data):
        self.total = self.total + len(data)
        #  print 'Collecting'
        self.buffer = self.buffer + data


        # self.server.queue.put(rep)


    def found_terminator(self):
        # print' Found a terminator'
        data = self.buffer
        self.buffer = ''

        # p = tdc.InquiryProtocol()    # Just for arguments sake
        
        if self.in_payload:
            self.in_payload = False       # kill the payload flag
            res = self.packet.process(data)

            #self.packet.setpayload(data)
            
            self.set_terminator(1)
            
            # rep = 'tdcproxy_sender:-cc:-%d bytes:-%d' % ( self.channel_counter, self.total)
         
            self.server.report('s%d' % self.id ,'  %s :- %s' % ( self.packet.protocol, self.packet.command ) )      

            # Shunt the packets to the reciever
            if self.receiver.opened:                                        # Don't send if the receivers closed down..
                self.receiver.push(self.packet.getpacket())

        else:
            #print 'Sender data:',
            if data=='\x47':                                                                  # First byte of magic byte

                self.set_terminator(tdc.size_header_data -1)   # pull in the Sorel header
                return
            elif  data[0] =='\xAA':                                                        # Second byte of magic byte
                # A possible magic
                try:
                     # print 'Making a packet'
                     self.packet =  tdc.tdcpacket('\x47' + data)
                     #print ' Made a packet'
                     #print self.packet
                except:
                    tdc.error( 'unrecognized sender Header')
                    self.set_terminator(1)
                else:
                    # print 'protocol = ',self.packet.protocol, ' ', 
                    self.in_payload = True
                    self.set_terminator(self.packet.size_payload)
            else:
                self.set_terminator(1)


    def handle_close(self):
        print 'handling close'
        self.close()

    def sendmessage(self, protocol, command,  data='' ):
        try:
            prot = protocol.getreq(command)
        except ( KeyError ):
            tdc.error('Unknown command %s for protocol %s' %( command , protocol.desc))
            return -1

        payload = command + data
        plsize = self.payloadsize(payload)

       
        msg = protocol.Magic + protocol.flags + protocol.id + protocol.extra_header_size + plsize + protocol.extra_header_data + protocol.crc + payload


        # print 'Msg:-',msg

        #  assert(False)

      #  try:
            #self.s.send(msg)

        self.push(msg)





        
      #  except socket.timeout:
      #      error('A SEND TIMEOUT')
        
        #self.push(packet.getpacket())
        # assert(False)

    def payloadsize(self,  payload):
         plsize = len (payload)
         msb,lsb = divmod(plsize, 0x100)
         return chr(lsb)+chr(msb)


    
        
if __name__ =='__main__':

    
    sleep_time = 10      
    tdcps = tdcproxy_sender()
   
    print 'Starting the loop'
    while (1):
        asyncore.loop(timeout = 1, count= 2)
        # print 'Around loop'


        tdcps.sendmessage(tdc.ip ,'v?')

        time.sleep(sleep_time)


    

