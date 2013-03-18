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
        self.ack_number = 0

        self.server_ack = 0

        self.window = 0

        self.flag = 'SYN'


 