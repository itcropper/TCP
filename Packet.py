#-Packet-----------------------------------------------------------
FLAGS = ['ACK', 'SYN', 'SYNACK', 'RESET', 'PUSH', 'FIN']

class Packet:


    def __init__(self, message, to):
        
        self.to_addr = to[0]
        self.to_port = to[1]

        if message:
        	self.length = len(message)
        else:
        	self.length = 0
        self.body = message
        
        self.sent_at = 0

        self.seq_number = 0

        self.server_ack = 0

        self.flag = 'SYN'

        self.key = self.set_key(None)


    def set_key(self, key):
        if key != None and (self.seq_number == 0 and self.server_ack == 0):
            self.key = key
        elif self.seq_number == 0:
            self.key = self.server_ack
        else:
            self.key = self.seq_number
