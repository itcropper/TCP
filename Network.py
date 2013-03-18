
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from datetime import datetime
import os
import sched
import random

class Scheduler:
    
    current = 0
    
    def __init__(self):
        self.current = 0
        self.scheduler = sched.scheduler(Scheduler.current_time,Scheduler.advance_time)
    
    @staticmethod
    def current_time():
        return Scheduler.current

    @staticmethod
    def advance_time(units):
        Scheduler.current += units

    def add(self,time,event,handler):
        #print "added to scheduler: " + str(time)
        return self.scheduler.enterabs(time,1,handler,[time,event])

    def cancel(self,event):
        self.scheduler.cancel(event)

    def run(self):
        self.scheduler.run()

        
#-Link-----------------------------------------------------------
    

class Link:
    def __init__(self, scheduler, source, dest):
        
        self.source = source
        self.source.link = self
        self.dest = dest

        self.speed_of_electricity = 200000000.0 #rate at wich data can travel through the link.
        self.rate_of_link = 1000.0              #R, rate of link, in bits/second
        self.length_of_link = 100000.0          #length that packets have to travel in Meters
        self.queue = Queue()                    #represents the queue, storing packets to be dealt with
        self.queue_threshHold = 256             #represents the max # of packets that can be store in the queue
        self.sked = scheduler                   
        self.unlimited = True

        self.link_is_not_busy = True

        self.packet_dropper = random.random()
        
    def enqueue(self, t, pack):
        
        

        if self.queue_threshHold > self.queue.qsize() or self.unlimited:
            if self.queue.empty() and self.link_is_not_busy:
                self.link_is_not_busy = False
                self.sked.add(t , pack, self.transmission_handler)
            self.queue.put(pack)            
        
    def transmission_handler(self, t, pack):

        #print ("TIME: " + str(t))

        packet = self.queue.get()

        '''
        if packet.body:
            print("transmission handler = " + str(packet.seq_number))

        
        if packet.body:
            print ("SENDING Message: " + packet.body)
        '''
        #print ("link.transmission_handler")

        
        #packet came off the queue, so calculate queuing delay with now - start
        #packet[0].queing_delay = t - packet[0].start   Not Needed!

        #calculate transmissionDelat (L/R)
        #print packet
        transmission_delay = packet.length / self.rate_of_link
        
        #add current Time to transmission delay
        newTime = t + transmission_delay
        
        #store transmission delay in packet
        #packet.trans_delay = transmission_delay   Not Needed

        will_drop_packet = random.randrange(0, 99, 1)
        if will_drop_packet > -1:
            #schedule to calculate propogation delay with the packet just popped.
            self.sked.add(newTime, packet, self.propagation_handler)
        
        #check of queue is empty
        if self.queue.qsize() > 0:
            
            #if not, then add an event to the scheduler for the transmission delay.
            self.sked.add(newTime, packet,self.transmission_handler)
            
        
    def propagation_handler(self, t, packet):
        
        self.link_is_not_busy = True
        
        #calculate propgation Delay (m/s)
        
        propogation_delay = self.length_of_link / self.speed_of_electricity

        #packet.prop_delay = propogation_delay
        
        self.sked.add(t + propogation_delay,
                      packet,
                      self.dest.socket.store)   #where is it going??????????????????????????????????

#-'Static'-ish printing to file class----------------------------------------------    
        
class printOut:
    def __init__(self, filename):
        self.file = filename
        self.open()

    
    def open(self):
        self.f = open(self.file, 'a')
        self.f.write("")
        self.f.write("")
        
    def close(self):
        self.f.close()
        
    def write(self, info):
        for peice in info:
            self.f.write(str(peice)+ " ")
        self.f.write("")   
            
