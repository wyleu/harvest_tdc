"""tdcproxy_server.py"""

import asyncore
import socket
import time
import Queue

from tdcproxy_receiver import *



class tdcproxy_server(asyncore.dispatcher):
    # The server for the proxy collects incoming messages and uses select to chuck them to a handler
    count = 0

    def __init__(self, host, port, queue, sender = None):     
        asyncore.dispatcher.__init__(self)
        self.sender = sender
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.there = (host, port)
        here = ('', port)     # Listen on any local port
        self.queue = queue
        self.msg=  {}
        try:
            self.bind(here)
        except socket.error, fred:
            print 'Socket Error :-', fred
            raise socket.error
        else:
            print ' Starting a server listening at %s, %d' %(here)
            self.listen(5)

    def handle_accept(self):

                ##accept(  	)
                ##    Accept a connection.
                ##    The socket must be bound to an address and listening for connections.
                ##    The return value is a pair (conn, address) where
                ##    conn is a new socket object usable to send and receive data on the connection, and
                ##    address is the address bound to the socket on the other end of the connection.
        
        accept = self.accept()
        #  self.report('srv','Handle accepted %s' % (accept,))
        self.receiver = tdcproxy_receiver(self, accept)
        if self.sender:
            self.sender.server = self
            self.sender.receiver = self.receiver


##    def __repr__(self):
##        try:
##            peer = self.getpeername()
##        except socket.error:
##            peer = ' Not connected yet'
##        return 'tdcproxy_server, listening on %s' % peer

    def report(self, channel, msg):
        l2 = []
        self.msg[channel] = msg
        l =self.msg.items()
        l.sort()
        for item in l:
            l2.append('%s %s' % (item[0], item[1]))
        string = ''.join(l2)
            

        self.queue.put(string)
        


if __name__ == '__main__':

    def processIncoming(queue):
        """ Handle all the messages in the queue"""
        while queue.qsize():
            try:
                msg = queue.get(0)
                # Check the contents and do stuff with it
                print  msg

            except Queue.Empty:
                # Shouldn't really happen
                pass
            
    sleep_time = 1
    queue = Queue.Queue()




    import tdcproxy_sender
    sender = tdcproxy_sender.tdcproxy_sender()
    sender.sendmessage(tdc.ip ,'v?')
    asyncore.loop(timeout = 1, count= 2)




    

    try:
        tdcproxy_server('192.168.0.50',10001,queue, sender)
    except socket.error, fred:
        print 'Socket error',socket.error, fred
        time.sleep(sleep_time)
        sleep_time = sleep_time * 2
        print 'Sleeping for :- ' ,sleep_time
    else:
        while (1):
              asyncore.loop(timeout = 1, count = 2)
              processIncoming(queue)

    

    
