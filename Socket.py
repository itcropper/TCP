from Packet import Packet, FLAGS
import sys
import random
import os

class host:

    def __init__(self, remote, scheduler):
        self.address = remote[0]
        self.port = remote[1]
        self.ip = remote[0]   
        self.remote = remote
        self.link = None
        self.scheduler = scheduler    

    def socket(self, domain, type):
        self.socket = Socket(domain, type, self)
        self.socket.sched = self.scheduler
        return self.socket;



#-SOCKET-----------------------------------------------------------

sockets = {}

__SYN_SENT__ = "SYN_SENT"
__SYN_RCVD__ = "SYN-RECEIVED"
__ESTABLISHED__ = "ESTABLISHED"
__FIN_WAIT_1__ = "FIN_WAIT_1"
__FIN_WAIT_2__ = "FIN_WAIT_2"
__CLOSE_WAIT__ = "CLOSE_WAIT"
__CLOSING__ = "CLOSING"
__LAST_ACK__ = "LAST_ACK"
__TIME_WAIT__ = 'TIME_WAIT'
__CLOSED__ = 'CLOSED'




class Socket:
    
    def __init__(self, domain, type, host):
        self.domain = domain
        self.remote = ('', '')
        self.type = type
        if self.domain == "SOCK_STREAM":
            pass
        elif self.domain == "SOCK_DGRAM":
            pass
        self.host = host
        self.buffer = ''
        self.packet_number = 0
        self.sched = None
        self.window_size = 20
        self.cache = {}
        self.time_out = .01
        self.STATE = __CLOSED__
        self.waiting_to_hear_about = {}


    def bind(self, remote):
        if not remote in sockets.keys():
            sockets[remote] = self
            self.remote = remote
        else:
            raise 'address and port already in use'
        

    def connect(self, connect_handler):
        #create SYN packet
       # print ("I AM A CLIENT")
        self.type = "CLIENT"
        packet = Packet(None, (self.host.address, self.host.port))
        packet.flag = "SYN"

        self.STATE = __SYN_SENT__

        print ("LISTEN <- SYN")

        #put SYN packet on the link
        self.sched.add(self.current_time(), packet, self.send_data)
        #print "sent: " + str(packet.fla)
        
        self.connect_handler = connect_handler
        
    def accept(self, accept_handler):
        #print ("I AM A SERVER!")
        self.type = "SERVER"
        socket = self
        self.accept_handler = accept_handler
        

    def send(self, flag, message):
        #print ("\nTYPE = " + self.type)

        self.send_buffer = message

        if self.remote == None:
            raise 'must call "bind()" first'

        #client initializes connection


        elif flag == None and self.type == "CLIENT" and self.STATE == "ESTABLISHED":

            buffer = []

            while len(message) > 0:
                buffer.append(message[:self.window_size])
                if len(message) < self.window_size:
                    message = ''
                else:
                    message = message[self.window_size:len(message)]

            for s in buffer:
                pack = Packet(s, self.remote)
                pack.flag = None
                pack.seq_number = self.packet_number
                top_data = pack.seq_number + pack.length
                print ("-> data " + str(pack.seq_number) + " - " + str(top_data))

                self.packet_number = top_data

                self.cache[pack.seq_number + pack.length] = pack

                self.sched.add(self.current_time(), pack, self.send_data)

              
    def send_data(self, time, packet):
        #print ("TIME: " + str(time))
        packet.sent_at = time
        self.__clocker(time, packet, self.host.link.enqueue)
        #s = raw_input("State = " + self.STATE)



    def recv(self, handle_recv):
        #handle_recv(self, socket, message):
        self.recv_handler = handle_recv

    def close(self):
        print ("SOCKET CLOSED")
        self.host.socket = None

    def done(self):
        print ("Socket Closed")
        pass


    def store(self, time, packet):

        #print ("TYPE:" + self.type, "FLAG:" + str(packet.flag), "STATE: " + self.STATE + "\n")
        print ("\n")
        if packet.body:
            self.buffer = packet.body

        if self.type == "SERVER":

            #Client sent out ACK, now server is fully connected
            if packet.flag == "ACK" and self.STATE == __SYN_RCVD__:

                print("ACK-RCVD")
                print("SERVER CONNECTED...")
                self.STATE = __ESTABLISHED__
                a = self
                self.accept_handler(self.current_time(), a)

            elif packet.flag == "ACK" and self.STATE == __ESTABLISHED__:
                pack = Packet(None, self.remote)
                pack.flag = "ACK"

                self.STATE == __CLOSE_WAIT__
                self.sched.add(self.current_time(), pack, self.send_data)

            elif packet.flag == "ACK" and self.STATE == __LAST_ACK__:
                self.STATE == __CLOSED__
                print (__LAST_ACK__, "->", __CLOSED__, "\n")
                return


            elif packet.flag == None:
                if self.packet_number  == packet.seq_number or True:
                    #print (self.packet_number, packet.seq_number, packet.length)
                    #s = raw_input("self.packet_number  == packet.seq_number")
                    pack = Packet(None, self.remote)
                    pack.flag = "ACK"
                    #print (packet.seq_number)
                    pack.server_ack = packet.seq_number + packet.length
                    self.packet_number = pack.server_ack
                    #print ("Packet Number: " + str(self.packet_number))
                    print ("<- ack " + str(pack.server_ack))
                    self.sched.add(self.current_time(), self.buffer, self.recv_handler)
                    self.sched.add(self.current_time(), pack, self.send_data)
                else:
                    #print (self.packet_number, packet.seq_number, packet.length)
                    #s = input("self.packet_number !!!= packet.seq_number")
                    self.cache[packet.seq_number] = packet
                    pack = Packet(None, self.remote)
                    pack.flag = "ACK"
                    #print (packet.seq_number)
                    pack.server_ack = self.packet_number + pack.length
                    self.packet_number = pack.server_ack
                    print ("<- ack " + str(pack.server_ack))
                    self.sched.add(self.current_time(), self.buffer, self.recv_handler)
                    self.sched.add(self.current_time(), pack, self.send_data)

            elif packet.flag == "FIN" and self.STATE == __ESTABLISHED__:
                pack1 = Packet(None, self.remote)
                pack1.flag = "ACK"
                self.STATE == __CLOSE_WAIT__
                print (__ESTABLISHED__, "->", __CLOSE_WAIT__)
                self.sched.add(self.current_time(), pack1, self.send_data)
                pack2 = Packet(None, self.remote)
                pack2.flag = "FIN"
                self.STATE = __LAST_ACK__
                print (__CLOSE_WAIT__, "->", __LAST_ACK__)
                self.sched.add(self.current_time(), pack2, self.send_data)

            elif packet.flag == "SYN" and self.STATE == __CLOSED__:
                
                self.STATE = __SYN_RCVD__

                pack = Packet(None, self.remote)
                pack.flag = "SYNACK"
                print("SYN-RCVD -> SYN+ACK")
                self.sched.add(self.current_time(), pack, self.send_data)
                '''
                pass
                '''

        #Must be a client
        else:
            if packet.flag == "ACK" and self.STATE == "ESTABLISHED":
                print ("CLIENT RECVD ", packet.server_ack, "\n")


                if False:
                    seq = self.cache[packet.server_ack].seq_number
                    length = self.cache[packet.server_ack].length
                    print ("-> retransmit  " +
                            str(seq) 
                            + " - " + 
                            str(seq + length))

                    self.sched.add(self.current_time(), self.cache[packet.server_ack], self.send_data)
                    
                    #print ("Packets still to be sent")
                    #for p in self.cache.keys():
                    #    print (self.cache[p].body)
                elif False:
                    #store in a cache somehow
                    print ("SHOULDN'T GET HERE YET")
                    pass
                else:
                    print "finishing early?"
                    self.sched.add(self.current_time(),self.buffer, self.recv_handler )
                    del self.cache[packet.server_ack] 

                    if len(self.cache) == 0:
                        print (__ESTABLISHED__, " ->",__FIN_WAIT_1__, "\n")
                        pack = Packet(None, self.remote)
                        pack.flag = "FIN"
                        self.STATE = __FIN_WAIT_1__
                        self.sched.add(self.current_time(), pack, self.send_data)
                        


                    #Client recieved SYNACK from server, now client is fully connected
            elif packet.flag == "ACK" and self.STATE == "FIN_WAIT_1":
                print (__FIN_WAIT_1__, " ->", __FIN_WAIT_2__, "\n")
                self.STATE = __FIN_WAIT_2__
                pack = Packet(None, self.remote)
                pack.flag = "ACK"
                self.sched.add(self.current_time(), pack, self.send_data)



            elif packet.flag =="SYNACK" and self.STATE == "SYN_SENT":
                
                self.STATE = __ESTABLISHED__
                pack = Packet(None, self.remote)
                pack.flag = "ACK"
                print("SYN+ACK-RCVD <- ACK")
                #print ("CLIENT CONNECTED...")
                self.STATE = __ESTABLISHED__
                self.sched.add(self.current_time(), pack, self.send_data)
                self.connect_handler()
            
            elif packet.flag == "FIN" and self.STATE == __FIN_WAIT_2__:
                pack = Packet("FINISHED", self.remote)
                pack.flag = None
                self.STATE = __TIME_WAIT__
                self.sched.add(self.current_time(), (0, pack), self.time_wait)

    def time_wait(self, time, data):
        if data[0] == 1:
            self.STATE = __CLOSED__
            print (__TIME_WAIT__, "->", __CLOSED__, "\n")
            self.close()
        else:
            data = (data[0] + 1, data[1])
            self.sched.add(self.current_time(), data, self.time_wait)


    def __clocker(self, time, packet, function):


        
        #self.sched.add(time + self.time_out, packet, __clocker)

        self.sched.add(time, packet, function)

    def current_time(self):
        return self.sched.current_time()