
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
from typing import Literal, Text, Union
import json
from settingsfile import *
dir = "data/"
FPS = 60
TOP = "top"
MIDDLE = "middle"
BOTTOM = "bottom"
INTERACTIVERANGE = 60


def d(debug):
    """global debugging"""
    print(debug)

def delete(obj):
    del obj



class GameObject:
    def __init__(self, img_path, width, height, xpos, ypos, interactive:bool = False):
        self.id = uuid4()
        self.img_path = img_path
        self.width = width
        self.height = height    
        self.img = transform.scale(image.load(img_path), (self.width, self.height))
        self.xpos = xpos
        self.ypos = ypos
        self.interactive = interactive
        self.group = None
        self.alive = True
        
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

    def flip(self,horizontal: bool, vertical: bool):
        self.img = transform.flip(self.img, horizontal, vertical)
        
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

    def destroy(self):
        self.group - self
        delete(self)

    def interact(self, gameobject, game):
        return

    def kill(self):
        self.alive = False
        self.destroy()


class Destructible(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)

    def interact(self, gameobject, game):
        self.destroy()


class Killable(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)

    def interact(self,gameobject, game):
        gameobject.kill()


class Goldore(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)

    def interact(self, gameobject, game):
        self.destroy()
        game:Game
        game.gold + 10

       
class Silberore(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)

    def interact(self, gameobject, game):
        self.destroy()
        game: Game
        game.silber + 10
        

        

class Player(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos):
        super().__init__(img_path, width, height, xpos, ypos)
        self.flipped = FLIPPEDLEFT
        self.alive = True
    
    def in_heigh_focus(self,move_tuple:tuple):
        LOCALDEBUG = False
        def ld(txt):
            if LOCALDEBUG:
                print(txt)
            
        x_move, y_move = move_tuple
        x_contra = y_contra = 0
        rt = []
        if self.xpos + x_move < WIDTH*0.1:
            ld(f"object out of focus: left")
            x_contra = MOVESPEED
            x_move = 0 
        elif self.xpos + self.width +x_move > WIDTH*0.9: 
            x_contra = -MOVESPEED
            x_move = 0
            ld(f"object out of focus: right")
        if self.ypos + y_move < HEIGHT*0.1:
            y_contra = MOVESPEED
            y_move = 0
            ld(f"object out of focus: top")
        elif self.ypos + self.height+ y_move > HEIGHT*0.9:
            y_contra = -MOVESPEED
            y_move = 0
            ld(f"object out of focus: bottom")
       
        rt.append((x_move,y_move))
        rt.append((x_contra,y_contra))
        return rt


    def move(self,movetup):
        super().move((movetup))
        x_move , _ = movetup
        if x_move < 0 and self.flipped == FLIPPEDRIGHT:
            self.flip(True, False)
            self.flipped = FLIPPEDLEFT
        elif x_move > 0 and self.flipped == FLIPPEDLEFT:
            self.flip(True, False)
            self.flipped = FLIPPEDRIGHT

   
    
class ObjectGroup:
    def __init__(self, surface : Surface, active:bool = True) -> None:
        self.list: list[Union[GameObject,Player]] = []
        self.surface = surface
        self.active = active

    def add(self, gameobject : GameObject):
        self.list.append(gameobject)

    def draw(self):
        if self.active:
            for obj in self.currently_on_screen():
                self.surface.blit(obj.img, (obj.xpos, obj.ypos))

    def get_list(self):
        return self.list

    def __sub__(self, gameobject:GameObject):
        self.list.remove(gameobject)
        return self

    def __add__(self, gameobject : GameObject):
        self.list.append(gameobject)
        gameobject.group = self
        return self

    def move(self, move_tuple:tuple):
        for obj in self.list:
            obj.move(move_tuple)


    def currently_on_screen(self) -> list:
        """returns all GameObjects which need to be drawn"""
        rtl = []
        for obj in self.list:
            x1 = (obj.x_right < 0)
            x2 = (obj.xpos > WIDTH)
            y3 = (obj.y_bottom < 0)
            y4 = (obj.ypos > HEIGHT)
            if x1 or x2 or y3 or y4:    
                continue
            rtl.append(obj)
        return rtl
            

    def __repr__(self) -> str:
        return self.list

    def collision_precheck(self,gameobject: Union[GameObject,Player], move_tuple: tuple):
        """checks whether a GameObject or Player Object collides with a child of the ObjectGroup\n
        return a tuple with the maximum allowed move values """
        
        x_move,y_move = move_tuple
        rtvalx, rtvaly = move_tuple
        LOCALDEBUG = False
        def ld(txt):
            """method intern debugging"""
            if LOCALDEBUG: 
                print(txt)

        for obj in self.list:
            x1 = (obj.xpos < gameobject.xpos + x_move < obj.x_right)
            x2 = (obj.xpos < gameobject.x_right + x_move < obj.x_right)

            y3 = (obj.ypos < gameobject.ypos + y_move < obj.y_bottom)
            y4 = (obj.ypos < gameobject.y_bottom + y_move < obj.y_bottom)
         
            if y_move != 0:
                if (x1 or x2) and y3 and (not y4):  
                    rtvaly = obj.y_bottom- gameobject.ypos                   
                    ld("top")
                elif (x1 or x2) and y4 and (not y3):
                    rtvaly = obj.ypos - gameobject.y_bottom                  
                    ld("bottom")
        
                if abs(rtvaly) > MOVESPEED:
                    rtvaly = y_move
                y_move = rtvaly

            if x_move != 0:
                if x2 and (y3 or y4) and (not x1):     
                    rtvalx = obj.xpos- gameobject.x_right         
                    ld("right")
                elif x1 and (y3 or y4) and (not x2):
                    rtvalx = obj.x_right - gameobject.xpos
                    ld("left")
               
                if abs(rtvalx) > MOVESPEED:
                    rtvalx = x_move
                x_move = rtvalx
                
        return (x_move,y_move)


    def interactive_in_range(self, gameobject:GameObject|Player):
        rtl = []
        for obj in self.list:
            if not obj.interactive:
                continue
            x1 = (obj.xpos - INTERACTIVERANGE < gameobject.xpos < obj.x_right+ INTERACTIVERANGE)
            x2 = (obj.xpos - INTERACTIVERANGE < gameobject.x_right  < obj.x_right + INTERACTIVERANGE)

            y3 = (obj.ypos - INTERACTIVERANGE < gameobject.ypos < obj.y_bottom + INTERACTIVERANGE)
            y4 = (obj.ypos - INTERACTIVERANGE < gameobject.y_bottom  < obj.y_bottom+ INTERACTIVERANGE)

            if (x1 or x2) and (y3 or y4):
                rtl.append(obj)
        ln = len(rtl)
        if ln == 0:
            return None
        elif ln == 1:
            return rtl[0]
        else:
            l = abs(rtl[0].xpos - gameobject.xpos)
            x = 0
            for ind, rt in enumerate(rtl):
                ll = abs(rt.xpos - gameobject.xpos)
                if ll < l:
                    l = ll
                    x = ind
            return rtl[x]

    def is_active(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def toggle(self):
        if self.active:
            self.active = False
        else:
            self.active = True


    




class ToggleGroup(ObjectGroup):
    def __init__(self, surface: Surface, active:bool) -> None:
        super().__init__(surface)
        self.active = active
    
    def is_active(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def toggle(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def draw(self):
        if self.active:
            super().draw()



class TextBox(GameObject):
    def __init__(self, text, color, fontsize, width, height, xpos, ypos, fontstyle: str = "Calibri"): 
        self.text = text
        self.color = color
        self.fontsize = fontsize
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.fontstyle = fontstyle
        self.update_vals()
        self.font = font.SysFont(self.fontstyle, self.fontsize, True, False)
        self.img = self.font.render(self.text, True, self.color)


    def update_text(self,text):
        self.text = text
        self.rerender()
    

    def rerender(self):
        self.img = self.font.render(self.text, True, self.color)  



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
            #inqueue.put({data1:data2})
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




class Item:
    def __init__(self,name, color,amount) -> None:
        self.name:str = name   
        self.amount:int = amount
        self.color = color
        self.id = uuid4()
        self.text = self.get_text()

    def get_text(self):
        return f"{self.name} {self.amount}"

    def add(self,amount:int):
        self.amount += amount

    def sub(self, amount:int):
        self.amount -= amount
    
    def __add__(self, amount:int):
        self.amount += amount
        return self

    def __sub__(self, amount:int):
        self.amount += amount
        return self

class Gold(Item):
    def __init__(self, amount) -> None:
        name = "Gold "
        color = GOLD
        super().__init__(name,color, amount)


class Silber(Item):
    def __init__(self, amount) -> None:
        name = "Silber "
        color = SILBER
        super().__init__(name, color, amount)
        
        
class ItemBox(TextBox):
    def __init__(self, item:Item, fontsize, width, height, xpos, ypos, fontstyle: str = "Calibri"):
        super().__init__(item.get_text(), item.color, fontsize, width, height, xpos, ypos, fontstyle)
        self.item = item
        
    def update_text(self):
        return super().update_text(self.item.get_text())





class Game:
    def __init__(self) -> None:

        self.objdict = {BOTTOM:[], MIDDLE:[], TOP:[]}
        self.objdict_keys = [BOTTOM,MIDDLE,TOP]
           
        
        pg.init()
        self.WIN = display.set_mode((WIDTH, HEIGHT))

        pg.display.set_caption("yeye")

        self.bg = ObjectGroup(self.WIN)
        red = GameObject(dir+"red.png", 1000,1000,0,0)
        self.bg + red
        self.objdict[BOTTOM].append(self.bg)

        self.player = ObjectGroup(self.WIN)
        self.player1 = Player(dir+"player1.png", 100,86,500,200)
        self.player + self.player1
        self.objdict[TOP].append(self.player)
        
        self.obstacles = ObjectGroup(self.WIN)
        obst1 = GameObject(dir+"img1.png", 200,200,400,400, True)
        obst2 = GameObject(dir+"blue.png", 100,200,500,600)
        dest1 = Destructible(dir+"green.png", 1000,80,20,20,True)
        kill1 = Killable(dir+"green.png", 1000,1000, -2000,0, True)
        gold1 = Goldore(dir+"blue.png", 200,200,1000,200, True)
        silber1 = Silberore(dir + "green.png", 200,200,1000,600, True)
        self.obstacles + obst1
        self.obstacles + obst2
        self.obstacles + dest1
        self.obstacles + kill1
        self.obstacles + gold1
        self.obstacles + silber1
        self.objdict[MIDDLE].append(self.obstacles)

        hforhelp = TextBox("Press 'H' for help", WHITE, 30,100,100,475,20)
        self.hud = ObjectGroup(self.WIN, True)
        self.hud + hforhelp
        self.objdict[TOP].append(self.hud)

        self.stbg = GameObject(dir+"black 95.png", WIDTH,HEIGHT, 0,0)
        stmenutxt = TextBox("Menu", WHITE, 60, 100, 100, 550,20)
        wmovement = TextBox("W <==> UP", GREEN, 40, 100, 100, 200,100)
        smovement = TextBox("S <==> DOWN", GREEN, 40, 100, 100, 200,200)
        amovement = TextBox("A <==> LEFT", GREEN, 40, 100, 100, 200,300)
        dmovement = TextBox("D <==> RIGHT", GREEN, 40, 100, 100, 200,400)
        interacthelp = TextBox("E <==> INTERACT", GREEN, 40, 100, 100, 200,500)
        

        self.stmenu = ObjectGroup(self.WIN, False)
        self.stmenu + self.stbg
        self.stmenu + stmenutxt
        self.stmenu + wmovement 
        self.stmenu + smovement 
        self.stmenu + amovement 
        self.stmenu + dmovement
        self.stmenu + interacthelp

        self.objdict[TOP].append(self.stmenu)

        self.gold = Gold(0)
        self.silber = Silber(0)

        self.inventorygroup = ObjectGroup(self.WIN, False)
        self.inventorybg = GameObject(dir+"gray 80.png", WIDTH/2,HEIGHT/2, WIDTH/4,HEIGHT/4)
        self.inventorygold = ItemBox(self.gold, 40, 50,50,self.inventorybg.xpos+20,self.inventorybg.ypos+40)
        self.inventorysilber = ItemBox(self.silber, 40, 50,50,self.inventorybg.xpos+20,self.inventorybg.ypos+100)
        self.inventorygroup + self.inventorybg
        self.inventorygroup + self.inventorygold
        self.inventorygroup + self.inventorysilber

        self.objdict[TOP].append(self.inventorygroup)

        
        
       
        self.clock = pg.time.Clock()
        self.movementkeys = {"w":[False,(0,-MOVESPEED)], "a":[False,(-MOVESPEED,0)], "d": [False,(MOVESPEED,0)], "s":[False, (0,MOVESPEED)]}
        self.overlaykeys: dict[str:function] = {"h":[False,False, self.togglehud], "e":[False, False, self.interact], "i":[False,False, self.toggleinventory]}

        self.mainloop()

    def toggleinventory(self):
        if not self.inventorygroup.is_active():
            self.activateinventory()
            self.deactivatehelp()     
        else:
            self.deactivateinventory()

    def activateinventory(self):
        self.inventorygroup.activate()
    
    def deactivateinventory(self):
        self.inventorygroup.deactivate()
        
    def deactivatehelp(self):
        self.stmenu.deactivate()
        self.hud.activate()

    def activatehelp(self):
        self.stmenu.activate()
        self.hud.deactivate()

    def togglehud(self):
        if not self.stmenu.is_active():
            self.activatehelp()
            self.deactivateinventory()
        else:
            self.deactivatehelp()


    def interact(self):
        rt:GameObject|None = self.obstacles.interactive_in_range(self.player1)
        if rt is None:
            return
        print("interaction")
        rt.interact(self.player1, self)
        
        



    def mainloop(self):

        def get_key_input():

            for event in pg.event.get():      
                if event.type == pg.KEYDOWN:
                    try:
                        self.movementkeys[event.unicode.lower()][0] = True
                    except:
                        try:
                            self.overlaykeys[event.unicode.lower()][0]= True             
                        except:
                            pass
                elif event.type == pg.KEYUP:
                    try:
                        self.movementkeys[event.unicode.lower()][0] = False
                    except:
                        try:
                            self.overlaykeys[event.unicode.lower()][0]= False
                        except:
                            pass
                elif event.type == pg.QUIT:
                    pg.quit()
                    exit()
        

        def handle_input():
            self.x_move = self.y_move = 0
            for item in self.movementkeys.values():
                if item[0] is True:
                    x,y = item[1]
                    self.x_move += x
                    self.y_move += y 

            for  item in self.overlaykeys.values():
                if item[0] and not item[1]:
                    item[2]()
                    item[1] = True
                elif not item[0]:
                    item[1] = False
            
            movement()
        

        def movement():
            collision = self.obstacles.collision_precheck(self.player1, (self.x_move,self.y_move))  
            focus = self.player1.in_heigh_focus((collision))
            self.player1.move(focus[0])
            self.bg.move(focus[1])
            self.obstacles.move(focus[1])


        def drawing():
            for key in self.objdict_keys:
                for obj in self.objdict[key]:
                    obj.draw()

        def update_items():
            self.inventorygold.update_text()
            self.inventorysilber.update_text()
            


        while True:
            
            self.clock.tick(FPS)
            
            get_key_input()

            if self.player1.alive:
                handle_input()

            update_items()
            
            self.WIN.fill("black")

            drawing()
            
            display.update()
        

def main():


    Game()


if __name__ == "__main__":
    main()