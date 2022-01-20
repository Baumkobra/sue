
import socket
from settingsfile import *
from headers import *
from messages import * 
from socket import AF_INET, SOCK_STREAM, socket
from multiprocessing import Process
from uuid import uuid4
from queue import Queue
from threading import Thread
import logging
from time import sleep 
run = True
def d(txt):
    print(txt)

class Server:
    def __init__(self) -> None:
        self.clientdict = {}
        self.server = socket(AF_INET,SOCK_STREAM)
        self.server.bind((HOST,PORT))
        d(f"binding socket on {HOST}:{PORT}")
        self.server.setblocking(True)
        self.server.listen()
        d(f"server listening on {HOST}:{PORT}")
        
        
     
        
    def accept(self) -> None:
        while run:
            
            d(f"accepting connection on {HOST}:{PORT}")
            sock, addr = self.server.accept()
            d(f"new connection accepted: {addr}")
            client = ServerClient(sock, addr)
            self.clientdict.update({client.id:client})




class ServerClient:
    def __init__(self, sock: socket, addr) -> None:
        self.id = uuid4()
        self.addr = addr
        self.sock : socket = sock
        d(f"new ServerClient object: id = {self.id}: addr = {self.addr}")
        self.get_message_process = Process(target=self.get_message, args=())
        return
        
    
    def receive(self):
        while True:
            data1, data2 = self.get_message()
            d(f"putting data in the queue: key:{data1} value:{data2}")
            queue.put({data1:data2})
            
    

    def get_message(self) -> tuple[str,str]:
        """receiving messages from a client"""

        d("awaiting new messages")

        header_data = self.sock.recv(HEADERSIZE)
        d(f"header received from {self.id}: {header_data}")

        header = decode_header(header_data)
        d(f"header decoded from {self.id}: {header}")

        raw_data = self.sock.recv(header)
        d(f"raw data received from {self.id}: {raw_data}")

        data1 , data2 = read_message(raw_data)
        d(f"data decoded from {self.id}: data1:{data1}, data2:{data2}")

        return data1.decode(), data2.decode()
            


def main():
    global server, queue
    server = Server()
    serveracceptthread = Process(target=server.accept)
    serveracceptthread.start()
    queue = Queue(5)

    




if __name__ == "__main__":
    main()


