
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
import json
from settingsfile import *
dir = "data/"
FPS = 60
WIDTH = 1200
HEIGHT = 1000


def d(debug):
    """global debugging"""
    print(debug)


class GameObject:
    def __init__(self, img_path, width, height, xpos, ypos):
        self.id = uuid4()
        self.img_path = img_path
        self.width = width
        self.height = height
        self.img = transform.scale(image.load(img_path), (self.width, self.height))
        self.xpos = xpos
        self.ypos = ypos
        self.update_vals()

    def update_vals(self):
        self.x_center = self.xpos + self.width /2
        self.y_center = self.ypos + self.height /2
        self.x_right = self.xpos + self.width
        self.y_bottom = self.ypos + self.height

        self.center = (self.x_center,self.y_center)
        self.top_right = (self.x_right, self.ypos)
        self.top_left = (self.xpos,self.ypos)
        self.bottom_right = (self.x_right, self.y_bottom)
        self.bottom_left = (self.xpos, self.y_bottom)

        
    def move(self,move_tuple: tuple):
        """move_tuple = (x_move,y_move)"""
        x_move, y_move = move_tuple
        self.xpos += x_move
        self.ypos += y_move
        self.update_vals()

    def move_to_position(self, position_tuple:tuple):
        x_pos, y_pos = position_tuple
        self.xpos = x_pos
        self.ypos = y_pos
        self.update_vals()

    def get_position(self):
        return (self.xpos,self.ypos)


class Player(GameObject):
    
    def in_heigh_focus(self,move_tuple:tuple):
        debug = False
        def ld(txt):
            if debug:
                print(False)
        x_move, y_move = move_tuple
        x_contra = y_contra = 0
        rt = []
        if self.xpos + x_move < WIDTH*0.2:
            ld(f"object out of focus: left")
            x_contra = MOVESPEED
            x_move = 0 
        elif self.xpos + self.width +x_move > WIDTH*0.8: 
            x_contra = -MOVESPEED
            x_move = 0
            ld(f"object out of focus: right")
        if self.ypos + y_move < HEIGHT*0.2:
            y_contra = MOVESPEED
            y_move = 0
            ld(f"object out of focus: top")
        elif self.ypos + self.height+ y_move > HEIGHT*0.8:
            y_contra = -MOVESPEED
            y_move = 0
            ld(f"object out of focus: bottom")
       
        rt.append((x_move,y_move))
        rt.append((x_contra,y_contra))
        return rt

    


class ObjectGroup:
    def __init__(self, surface : Surface) -> None:
        self.list: list[Union[GameObject,Player]] = []
        self.surface = surface

    def add(self, gameobject : GameObject):
        self.list.append(gameobject)

    def draw(self):
        for obj in self.currently_on_screen():
            self.surface.blit(obj.img, (obj.xpos, obj.ypos))

    def get_list(self, id):
        return self.list

    def __add__(self, gameobject : GameObject):
        self.list.append(gameobject)

    def move(self, move_tuple:tuple):
        for obj in self.list:
            obj.move(move_tuple)


    def currently_on_screen(self) -> list:
        """returns all GameObjects which need to be drawn"""
        rtl = []
        for obj in self.list:
            c1 = (obj.x_right < 0)
            c2 = (obj.xpos > WIDTH)
            c3 = (obj.y_bottom < 0)
            c4 = (obj.ypos > HEIGHT)
            if c1 or c2 or c3 or c4:    
                continue
            rtl.append(obj)
        return rtl
            

   

    def __repr__(self) -> str:
        return self.list

    def collision_precheck(self,gameobject: Union[GameObject,Player], move_tuple: tuple):
        """checks whether a GameObject or Player Object collides with a child of the ObjectGroup"""
        rtl = []
        x_move,y_move = move_tuple
     
        for obj in self.list:
            
            c1 = (obj.xpos < gameobject.xpos + x_move <= obj.x_right)
            c2 = (obj.xpos < gameobject.x_right + x_move <= obj.x_right)

            c3 = (obj.ypos < gameobject.ypos + y_move <= obj.y_bottom)
            c4 = (obj.ypos < gameobject.y_bottom + y_move <= obj.y_bottom)

                
            if (c1 or c2) and (c3 or c4):
                

                rtx = 0
                rty = 0
                """
                if c1 and c3:
                    #top left
                    print("top left")
                if c1 and c4:
                    #bottom left
                    print("bottom left")
                if c2 and c3:
                    #top right
                    print("top right")
                if c2 and c4:
                    print("bottom right")
                """
                if (c1 or c2) and c3 and not c4:  
                    rty = obj.y_bottom - gameobject.ypos
                    print("top")
                if (c1 or c2) and c4 and not c3:
                    rty = obj.ypos - gameobject.y_bottom
                    print("bottom")
                if c2 and (c3 or c4) and not c1:
                    rtx = obj.xpos - gameobject.x_right
                    print("right")
                if c1 and (c3 or c4) and not c2:
                    rtx = obj.x_right - gameobject.xpos
                    print("left")
                rtl.append((rtx,rty))
               
        if rtl == []:
            return False
        d(f"object {gameobject.id} collides with object {rtl}")
        return rtl
            
                


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
            d(f"putting data in the inqueue: key:{data1} value:{data2}")
            inqueue.put({data1:data2})
            d(f"put data in the inqueue")
    

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


    def update(self, gameobj: GameObject):
        id = gameobj.id
        data = gameobj.get_position()
        d(f"updating gameobj:{id.__str__()}")
        self.send_message(id.bytes,json.dumps(data).encode())





def mainloop():
    clock = pg.time.Clock()
    keydown = {"w":[False,(0,-MOVESPEED)], "a":[False,(-MOVESPEED,0)], "d": [False,(MOVESPEED,0)], "s":[False, (0,MOVESPEED)]}
    gl_pan = (0,0)
    while True:
        x_move = y_move = 0
        clock.tick(FPS)
        WIN.fill("black")
        bg.draw()
        obstacles.draw()
        player.draw()
        
        for event in pg.event.get():
            
            if event.type == pg.KEYDOWN:
                
                try:
                    keydown[event.unicode.lower()][0] = True
                except:
                    pass

            elif event.type == pg.KEYUP:
                try:
                    keydown[event.unicode.lower()][0] = False
                except:
                    pass

            elif event.type == pg.QUIT:
                pg.quit()
                exit()
        
        for _, item in keydown.items():
            if item[0] is True:
                x,y = item[1]
                x_move += x
                y_move += y
           
        focus = player1.in_heigh_focus((x_move,y_move))
        collision = obstacles.collision_precheck(player1, (x_move,y_move))
  
        if collision is False:
        
            player1.move(focus[0])
            bg.move(focus[1])
            obstacles.move(focus[1])
        else:
            for coltup in collision:
                player1.move(coltup)

        pg.display.update()
        


def main():
    global WIN, group, player, bg, inqueue, player1, outqueue, obstacles
   
    inqueue = Queue(maxsize=2)
    outqueue = Queue(maxsize=2)
    pg.init()
    WIN = display.set_mode((WIDTH, HEIGHT))
  
    pg.display.set_caption("yeye")

    bg = ObjectGroup(WIN)
    red = GameObject(dir+"red.png", 1000,1000,0,0)
    bg + red

    player = ObjectGroup(WIN)
    player1 = Player(dir+"player1.png", 100,86,500,200)
    player + player1
    
    obstacles = ObjectGroup(WIN)
    obst1 = GameObject(dir+"img1.png", 200,200,400,400)
    obst2 = GameObject(dir+"blue.png", 100,200,600,600)
    obstacles + obst1
    obstacles + obst2
    
    mainloop()
   

if __name__ == "__main__":
    main()