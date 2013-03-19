
from Socket import Socket, host
from Network import Link, Scheduler

AF_INET = "AF_INET"
SOCK_STREAM = "SOCK_STREAM"

class Server:
    def __init__(self, host, port):
        #print "TimeServer Init"
        self.socket = host.socket(AF_INET, SOCK_STREAM)
        self.socket.bind((host.ip, port))
        #print ("SERVER -> ACCEPT -> CLIENT")
        self.socket.accept(self.handle_connection)
    
    def handle_connection(self, time, socket):
        socket.recv(ServerConnection(socket).handle_recv)
        

class ServerConnection:
    def __init__(self, socket):
        self.socket = socket
        self.buffer = ''
    
    def handle_recv(self, socket, message):
        #print ("SERVER BUFFER:" + message)

        
        #print ("Server recieving message: \n'" + message + "'\n")
        #self.socket.close()
        pass

            
class Client:

    def __init__(self, host, remote):
        self.buffer = ''
        self.socket = host.socket(AF_INET, SOCK_STREAM)
        #print ("CLIENT -> CONNECT -> SERVER")
        self.socket.connect(self.handle_connection)
        #print ("timeClient.init")
        
    def handle_connection(self):
        #print "handle_connection: send"
        #print ("CLIENT BUFFER:" +self.socket.buffer)
        #name = raw_input("send something\n")
        self.socket.buffer = ""
        #print ("sending data from client")
        preamble = "We the people of the United States, in order to form a more perfect union, establish justice, insure domestic tranquility, provide for the common defense, promote the general welfare, and secure the blessings of liberty to ourselves and our posterity, do ordain and establish this Constitution for the United States of America."
        shorter = "We the people of the United States"
        self.socket.send(None, shorter)
        self.socket.recv(self.handle_recv)
        #self.socket.recv(self.handle_recv)
        
    def handle_recv(self, socket, message):
        #print ("Back at client" + message)
        pass
        


if __name__ == "__main__":

    #print ("main")

    sched = Scheduler()

    dest = host(('120.0.0.2', 8080), sched)
    source = host(('120.0.0.1', 8080), sched)


    linkA = Link(sched, source, dest)
    linkB = Link(sched, dest, source)

    s = Server(dest, ('120.0.0.2', 8080))
    c = Client(source, ('120.0.0.1', 8080))
    

    sched.run()
