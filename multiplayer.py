from multiprocessing import Process
from threading import Thread
from pygame import *
import pygame as pg
from pygame.sprite import *
from socket import socket, AF_INET, SOCK_STREAM
from pygame import image, transform, display
from os import getcwd
from uuid import uuid4
from socket import *
from headers import *
from messages import *
from queue import Queue
from settingsfile import *
from typing import Literal, Union
dir = "data/"
FPS = 60
WIDTH = 1200
HEIGHT = 1000

def d(debug):
    print(debug)


class GameObject:
    def __init__(self, img_path, width, height, xpos, ypos):
        self.id = uuid4()
        self.img_path = img_path
        self.width = width
        self.height = height
        self.img = image.load(img_path)
        self.img = transform.scale(self.img, (self.width, self.height))
        self.xpos = xpos
        self.ypos = ypos


    def move(self,x_move,y_move):
        self.xpos += x_move
        self.ypos += y_move



class ObjectGroup:
    def __init__(self, surface : Surface) -> None:
        self.list: list[GameObject] = []
        self.surface = surface

    def add(self, gameobject : GameObject):
        self.list.append(gameobject)

    def draw(self):
        for obj in self.list:
            self.surface.blit(obj.img, (obj.xpos, obj.ypos))

    def get_list(self, id):
        return self.list

    def __add__(self, gameobject : GameObject):
        self.list.append(gameobject)

    def __repr__(self) -> str:
        return self.list


class ServerClient:
    def __init__(self) -> None:
        """connecting to the server"""
        try:
            self.connection : socket= socket(AF_INET,SOCK_STREAM)
            d(f"attempting to connect to: {HOST}, {PORT}")
            self.connection.connect((HOST,PORT))
            d(f"established connection : {HOST}, {PORT}")
            self.connection.setblocking(True)

            self.receive_process = Process(target=self.receive, args=())
            d(f"starting receive_process")
            self.receive_process.start()    
        except Exception as ex:
            d(f"Exception on ServerClient__init__(): {ex}")
            d(f"exiting programm")
            exit()


    def receive(self):
        while True:

            data = self.get_message()
            if data is False:
                continue
            data1, data2 = data
            d(f"putting data in the queue: key:{data1} value:{data2}")
            queue.put({data1:data2})
            d(f"put data in the queue")
    

    def get_message(self) -> Union[tuple[str,str], Literal[False]]:
        """receiving messages from the server"""

        d("awaiting new messages")

        header_data = self.connection.recv(HEADERSIZE)
        d(f"header received: {header_data}")
        if header_data == b"":
            return False
        header = decode_header(header_data)
        d(f"header decoded: {header}")

        raw_data = self.connection.recv(header)
        d(f"raw data received: {raw_data}")

        data1 , data2 = read_message(raw_data)
        d(f"data decoded: data1:{data1}, data2:{data2}")

        return data1.decode(), data2.decode()

    
    def send_message(self, data1, data2) -> None:
        """sending a message to the server"""

        d(f"formatting for sending: data1:{data1}, data2:{data2}")

        formatted_data = format_message(data1=data1, data2=data2)
        d(f"formatted data: {formatted_data}")

        header = get_header(formatted_data)
        d(f"header created: {header}")

        self.connection.send(header)
        self.connection.send(formatted_data)
        d("sent data")

        




def mainloop():
    clock = pg.time.Clock()
    keydown = {"w":False, "a":False, "d": False, "s":False}
    while True:
        WIN.fill("black")
        clock.tick(FPS)
        
        players.draw()
        

        for event in pg.event.get():
            
            if event.type == pg.KEYDOWN:
                print(event.unicode)
                try:
                    keydown[event.unicode] = True
                except:
                    pass

            elif event.type == pg.KEYUP:
                try:
                    keydown[event.unicode] = False
                except:
                    pass

            elif event.type == pg.QUIT:
                pg.quit()
                exit()
        
        for key, item in keydown.items():
            if item is True:
                if key == "w":
                    player1.move(0,-10)
                elif key == "s":
                    player1.move(0,10)
                elif key == "a":
                    player1.move(-10,0)
                elif key == "d":
                    player1.move(10,0)

        pg.display.update()


def main():
    global WIN, group, players, bg, queue, player1
    client = ServerClient()
    queue = Queue(maxsize=2)
    pg.init()
    WIN = display.set_mode((WIDTH, HEIGHT))
  
    pg.display.set_caption("yeye")
    players = ObjectGroup(WIN)
    bg = ObjectGroup(WIN)
    player1 = GameObject(dir+"player1.png", 100,100,300,200)
    players + player1
   
    mainloop()
   

if __name__ == "__main__":
    main()