"""   TDC Handler   """

__doc__ =  '''Harvest TDC Handler - \xa9 wyleu 2008,2009

'''


import socket

Magic = '\x47\xaa'
flags  = '\x00\x00'       #  bit 0 :- CRC protected 

tdcprotocol = '\x00'

extra_header_size = '\x00'
payload_size = '\x00\x00'
extra_header_data = ''
crc = ''
payload_data=''
##
header_data = Magic + flags + tdcprotocol + extra_header_size + payload_size
size_header_data = len(header_data)
##
##print 'Header Data Size:-', size_header_data

debug = False



def error(msg):
    print msg


class protocol(object):
    protocols  = {}
    reqs = {}
    resp = {}
    def __init__(self):

        self.Magic = '\x47\xaa'
        self.flags  = '\x00\x00'       #  bit 0 :- CRC protected 

        self.protocol =  '\x00'
        self.extra_header_size = '\x00'
        self.payload_size = '\x00\x00'
        self.extra_header_data = ''
        self.crc = ''
        self.payload_data=''
        self.header_data = self.Magic + self.flags + self.protocol + self.extra_header_size + self.payload_size
        self.size_header_data = len(self.header_data)

        
        self.desc = 'A protocol'
        self.protocols[self.id] = self

    def __repr__(self):
        return self.desc

    def process(self, payload):
        try:
            self.command = payload[0]
            func = self.resp[self.command]
        except:
            error('Found an unknown key type %s in %s payload size %d' % (self.command, self.desc, len( payload[1:])))
            return 'An unkonwn payload of length %d' % (len(payload[1:]), )
        return func(payload[1:])

    def getreq(self, command):
        return self.reqs[command]

        

class InquiryProtocol(protocol):
    def __init__(self):
        self.id = '\x00'
        protocol.__init__(self)
        self.desc =  'Inquiry protocol'
        self.reqs = { 'v?' :  self.req_softversion,
                       'p?' :  self.req_supportedprotocols }

        self.resp = {'E' : self.res_error,
                             'p' : self.res_supportedprotocols,
                             'v' : self.res_softversion}
    

    

    def req_softversion(self):
        pass

    def req_supportedprotocols(self):
        pass

    def res_error(self, payload):
        return payload

    def res_softversion(self, payload):
        return payload[1:]    # Pull of the ='s sign

    def res_supportedprotocols(self, payload):
        return payload

ip = InquiryProtocol()    # instantiate ip 
        
class RemoteControlProtocol(protocol):
    def __init__(self):
        self.id = '\x01'
        protocol.__init__(self)

        self.desc =  'Remote control protocol'

        self.reqs = { 'k' :  self.req_key,
                       'd' :  self.req_display,
                       'q' : self.req_quit }
        
        self.resp = {'k': self.res_key,
                           'K' : self.res_key,
                            'l'  : self.res_led,
                           'd'  : self.res_display,
                           's'  :  self.res_s}
    


    def req_key(self, key, state):
        pass

    def req_display(self):
        pass

    def req_quit(self):
        pass

    def res_key(self, payload):
        return payload

    def res_led(self, payload):
        return payload

    def res_display(self, payload):
        return payload

    def res_s(self, payload):
        print 'Curious s detected:- %s' % payload
        return

rcp = RemoteControlProtocol()
        
class ParameterProtocol(protocol):
    def __init__(self):
        self.id = '\x02'
        protocol.__init__(self)

        self.desc =  'Parameter I/O protocol'

        self.reqs = { 'g' :  self.req_getparameter,
                       's' :  self.req_setparameter,
                       'e' : self.req_enumerate,
                       'i'  : self.req_getproperty}
        
        self.resp = {'E': self.res_enumerate,
                    'v'  : self.res_value}
    



    def req_getparameter(self, name):
        pass

    def req_setparameter(self, name, value):
        pass

    def req_enumerate(self, payload):
        pass

    def req_getproperty(self, payload):
        pass

    def res_enumerate(self, payload):
        return payload

    def res_value(self, payload):
        return payload


pp = ParameterProtocol()


    


class tdcpacket(protocol):
    def __init__(self, data):
        self.data = data
        if data.index(Magic) == 0:
            #print 'Found a Magic'
            # self.Magic = data[0:2]

            self.flags = data[2:4]
            # print 'Flags:-',self.flags
            # self.protocol = data[4]
            #  print ' Protocol bit about to be considered:-', ord(data[4])
            #  print 'Protocol Types I know about', protocol.protocols
            try:
                self.protocol = protocol.protocols[data[4]]
            except KeyError:
                error ('\n\n\n\nUn-recognised protocol\n\n\n\n\n')
                raise KeyError
            #print 'Protocol:-',self.protocol
            self.size_extra_header = self.getsmallint(data[5])
            #print 'Extra Header Size:-', self.size_extra_header
            self.size_payload = self.getint(data[6:8])
            #print 'Payload size:-', self.size_payload
         
        else:
            error('A tdcpacket Error')
            raise TypeError

    
    def getint(self, chars):
        byte0 = ord(chars[0])
        byte1 = ord(chars[1])
        return byte1 * 256 + byte0

    def getsmallint(self,char):
        return ord(char[0])

    def __repr__(self):
        return 'Packet:- %s len:- %d ' %   (self.protocol,self.size_payload)

    def setpayload(self,payload):
        self.payload = payload

    def process(self,payload):
        self.payload = payload
        self.command = payload[0]
        # print 'PROTOCOL:-', self.protocol
        return self.protocol.process(payload)
    

    def getpacket(self):
        return self.data + self.payload
    





import socket
import string


##class TDC(asyncore.dispatcher):
##    def __init__(self, host = '192.168.1.50' , port = 10001):
##        asyncore.dispatcher.__init__(self)
##        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##        self.s.settimeout(5)
##
##        self.s.connect((host,port))
##
##        # print 'TIMEOUT:-', self.s.gettimeout()
##        self.protocol = ip
##        try:
##            self.ident()
##        except socket.error:
##            print socket.error
##
##        
##
##    def fetch(self, no):
##        try:
##            return self.s.recv(no)
##        except socket.timeout:
##            error('A RECEIVE TIMEOUT')
##
##    def getbyte(self):
##        return self.fetch(1)
##
##    def getbytes(self):
##        byte0  = self.fetch(1)
##        byte1 = self.fetch(1)
##        return byte0 + byte1
##
##    def getnobytes(self,num):
##        return self.fetch(num)
##
##    def getsmallint(self):
##        return ord(self.fetch(1))
##
##    def getint(self):
##        byte0 = ord(self.fetch(1))
##        byte1 = ord(self.fetch(1))
##        return byte1 * 256 + byte0
##
##    def getchar(self):
##        return self.fetch(1)
##
##    def payloadsize(self, payload):
##         plsize = len (payload)
##         msb,lsb = divmod(plsize, 0x100)
##         return chr(lsb)+chr(msb)
##         
##         
##
##    def sendmessage(self, protocol, command , data = '',  **kw):
##        try:
##            prot = protocol.getreq(command)
##        except ( KeyError ):
##            error('Unknown command %s for protocol %s' %( command , protocol.desc))
##            return -1
##        payload = command + data
##        plsize = self.payloadsize(payload)
##       
##        msg = Magic + flags + protocol.id + extra_header_size + plsize + extra_header_data + crc + payload
##        print 'Sending:-',msg
##        if debug:
##            error(msg)
##        data = '\x47\xaa\x00\x00\x02\x00\x09\x00gsensor3\x00'
##        #for index,item in enumerate(msg):
##        #    print 'Built:-',ord(item),item,
##        #    print ' Static:-',ord(data[index]),data[index]
##
##        try:
##            self.s.send(msg)
##        except socket.timeout:
##            error('A SEND TIMEOUT')
##
##
##
##
##
##    def fetchmessage(self):
##        while(1):
##            if self.getbytes()==Magic:
##                if debug:
##                    print 'Got Magic bytes'
##                break
##            else:
##                pass
##                # error('Not Magic Byte')
##        flags = self.getint()
##        protocol = self.getbyte()
##        try:
##            self.protocol = self.protocol.protocols[protocol]
##        except KeyError:
##            error ('Un-recognised protocol')
##        extra_header_size = self.getsmallint()
##        payload_size = self.getint()
##        print 'payload size:-', payload_size
##        if debug:
##            print 'flags:-', flags, 'type:-', type(flags)
##            print 'protocol:-',protocol,'value:-',ord(protocol), 'type:-', type(protocol),'Description:-',  self.protocol.desc
##            print 'extra_header_size:-',extra_header_size, 'type:-', type(extra_header_size)
##            print 'payload_size:-',payload_size, 'type:-', type(payload_size)
##        if extra_header_size:
##            extra_header_data = self.getnobytes(extra_header_size)
##            if debug:
##                print 'extra_header_data:-',extra_header_data, 'type:-', type(extra_header_data)
##            
##        if flags:
##            crc = self.getint()
##            if debug:
##                print 'crc:-',crc, 'type:-', type(crc)
##        if payload_size:
##            payload_data = self.getnobytes(payload_size)
##            if debug:
##                print 'payload_data:-',payload_data, 'type:-', type(payload_data)
##
##        return payload_data
##
##
##
##    def ident(self):
##        try:
##            self.sendmessage(ip,'v?')
##            ret = self.fetchmessage()
##            print 'TDC device %s @ %s  ->%s' %(ret ,self.getpeername(),self.s.getsockname()  )
##            return ret
##        except:
##            False
##
##        
##            
##        


if __name__ =='__main__':
    
    tdc = TDC(host = '192.168.0.50')

    tdc.ident()

    tdc.sendmessage(pp,'g','sensor1\x00')

    
    ret = tdc.fetchmessage()
    print 'Value:-', ord(ret[len(ret)-4])


    for index,item in enumerate(ret):
        print 'Return:-',index, 'Value:-',ord(item),item

##
##    assert(False)
##
##    
##    tdc.sendmessage(pp,'g','sensor1\x00')
##    ret = tdc.fetchmessage()
##    print 'Value:-', ord(ret[len(ret)-4])
##
##
##    for index,item in enumerate(ret):
##        print 'Return:-',index, 'Value:-',ord(item),item
##
##
##
##
##
##    assert(False)
##    
##
##    # Press 
##    #tdc.sendmessage(rcp,'d', data = '')
##    tdc.sendmessage(pp,'e')
##    while (1):
##        ret =  tdc.fetchmessage()
##        print 'Back from fetchmessage First Char:->',ret,'< as an int:-', ord(ret[len(ret)-1]),'length of that lot:-',len(ret)
##
##
##  #  import time
##
##  #  time.sleep(1)
##
##   # Release
##   # tdc.sendmessage(rcp,'k', data = '\x02\x00')
##   # tdc.fetchmessage()
##    
##        
##        
##    
##    
##    
##        
##        
    

            
        
        


    
        

        
                  
            
            
    
        

            
        







