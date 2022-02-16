

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
TOP = "TOP"
OBSTACLE = "MIDDLE"
BACKGROUND = "BOTTOM"
PLAYERLAYER = "PLAYER"
INTERACTIVERANGE = 60


def d(debug):
    """global debugging"""
    print(debug)

def delete(obj):
    del obj





class GameObject:
    def __init__(self, img_path, width, height, xpos, ypos, interactive:bool = False, active:bool = True):
        self.type = "default"
        self.id = uuid4()
        self.img_path = img_path
        self.width = width
        self.height = height    
        self.img = transform.scale(image.load(img_path), (self.width, self.height)).convert_alpha()
        self.xpos = xpos
        self.ypos = ypos
        self.interactive = interactive
        self.group = None
        self.alive = True
        self.active = active
        
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

    def update_text(self,text):
        return

    def interact(self, gameobject, game):
        return

    def kill(self):
        self.alive = False
        self.destroy()

    def to_dict(self):
        return {"type":self.type,"img":self.img_path, "alive":self.alive,"width":self.width,"height":self.height, "xpos":self.xpos,"ypos":self.ypos,"interactive":self.interactive}

class Destructible(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)
        self.type = "destructible"

    def interact(self, gameobject, game):
        self.destroy()


class Killable(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)
        self.type = "killable"

    def interact(self,gameobject, game):
        gameobject.kill()


class Goldore(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)
        self.type = "goldore"

    def interact(self, gameobject, game):
        self.destroy()
        game:Game
        game.gold + 10

       
class Silberore(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, interactive: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive)
        self.type = "silberore"

    def interact(self, gameobject, game):
        self.destroy()
        game: Game
        game.silber + 10

        

class Player(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos):
        super().__init__(img_path, width, height, xpos, ypos)
        self.type = "player"
        self.flipped = FLIPPEDLEFT
        self.alive = True
    
    def in_heigh_focus(self,move_tuple:tuple):
        treshhold = 0.8
        top_treshhold = 1 - treshhold
        bot_treshold = treshhold
        LOCALDEBUG = False
        def ld(txt):
            if LOCALDEBUG:
                print(txt)
            
        x_move, y_move = move_tuple
        x_contra = y_contra = 0
        rt = []
        if self.xpos + x_move < WIDTH*top_treshhold:
            ld(f"object out of focus: left")
            x_contra = MOVESPEED
            x_move = 0 
        elif self.xpos + self.width +x_move > WIDTH* bot_treshold:
            x_contra = -MOVESPEED
            x_move = 0
            ld(f"object out of focus: right")
        if self.ypos + y_move < HEIGHT*top_treshhold:
            y_contra = MOVESPEED
            y_move = 0
            ld(f"object out of focus: top")
        elif self.ypos + self.height+ y_move > HEIGHT*bot_treshold:
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
    def __init__(self, surface : Surface, active:bool = True, layer = None) -> None:
        self.list: list[Union[GameObject,Player]] = []
        self.surface = surface
        self.active = active
        self.layer = layer
        self.id = uuid4()

    def add(self, gameobject : GameObject):
        self.list.append(gameobject)

    def draw(self):
        if self.active:
            for obj in self.currently_on_screen():
                if obj.active:
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

    def __iter__(self):
        return self.list.__iter__()


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


    def to_dict(self):
        dc = {
            "Layer":self.layer,
            "ObjectGroup":{
                "active":self.active,
                "Elements":[
                ]
            }
        }
        [dc["ObjectGroup"]["Elements"].append(obj.to_dict()) for obj in self.list]
        return dc



class Button(GameObject):
    def __init__(self, img_path, width, height, xpos, ypos, func,interactive: bool = False, active: bool = True):
        super().__init__(img_path, width, height, xpos, ypos, interactive, active)
        self.func = func
        

    def click(self,cords:tuple[float,float]):
        xcord,ycord = cords
        x1 = (self.xpos < xcord < self.x_right)
        y2 = (self.ypos < ycord < self.y_bottom)

        if x1 and y2:
            self.func()

    

    def to_dict(self):
        pass

        



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
    def __init__(self, text, color, fontsize, width, height, xpos, ypos, fontstyle: str = "Calibri", active = True): 
        self.text = text
        self.color = color
        self.fontsize = fontsize
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.fontstyle = fontstyle
        self.type = "textbox"
        self.active = active
        self.update_vals()
        self.font = font.SysFont(self.fontstyle, self.fontsize, True, False)
        self.img = self.font.render(self.text, True, self.color).convert_alpha()


    def update_text(self,text):
        self.text = text
        self.rerender()
    

    def rerender(self):
        self.img = self.font.render(self.text, True, self.color)  

    def to_dict(self):
        return {"type":self.type,"text":self.text, "color":self.color,"fontsize":self.fontsize,"fontstyle":self.fontstyle,"width":self.width,"height":self.height, "xpos":self.xpos,"ypos":self.ypos, "active":self.active}

        

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
    def __init__(self,name, color,amount=0) -> None:
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
        self.amount -= amount
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

class Sword(Item):
    def __init__(self, amount) -> None:
        name = "Sword "
        color = BLACK
        super().__init__(name, color, amount)
        
        
class ItemBox(TextBox):
    def __init__(self, item:Item, fontsize, width, height, xpos, ypos, fontstyle: str = "Calibri",active = True):
        super().__init__(item.get_text(), item.color, fontsize, width, height, xpos, ypos, fontstyle, active)
        self.item = item
        self.type = "itembox"

        
    def update_text(self, _):
        return super().update_text(self.item.get_text())

    def to_dict(self):
        return {"type":self.type,"item":self.item.name.lower().strip(), "color":self.color,"fontsize":self.fontsize,"fontstyle":self.fontstyle,"width":self.width,"height":self.height, "xpos":self.xpos,"ypos":self.ypos, "active":self.active}




class Objectloader:
    def __init__(self) -> None:
        pass

    def load_objdict_from_json(self, file):
        file = open(file, "r")
        data = json.load(file)
        file.close()
        return data
      
  

class Chunk:
    def __init__(self) -> None:
        self.loaded = []
    




class Game:
    def __init__(self) -> None:
        
        self.gold = Gold(0)
        self.silber = Silber(0)
        self.sword = Sword(0)

        self.objdict = {BACKGROUND:[], OBSTACLE:[],PLAYERLAYER:[] ,TOP:[]}
        self.objdict_keys = [BACKGROUND,OBSTACLE,PLAYERLAYER,TOP]
        self.obj_classes :dict[str, GameObject]= {"default":GameObject,"destructible":Destructible, "killable":Killable,"goldore":Goldore,"silberore":Silberore}
        self.txtobj_classes : dict[str,TextBox|ItemBox] = {"textbox":TextBox, "itembox":ItemBox}
        self.item_dict : dict[str,Item] = {"gold":self.gold ,"silber":self.silber, "sword":self.sword}
        
        
        pg.init()
        self.WIN = display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("yeye")

        self.clock = pg.time.Clock()
        self.movementkeys = {"w":[False,(0,-MOVESPEED)], "a":[False,(-MOVESPEED,0)], "d": [False,(MOVESPEED,0)], "s":[False, (0,MOVESPEED)]}
        self.overlaykeys: dict[str:function] = {"h":[False,False, self.togglehud], "e":[False, False, self.interact], "i":[False,False, self.toggleinventory], "f":[False,False, self.craft]}



        #loading player  from file
        playerdata = Objectloader().load_objdict_from_json(PLAYER)
        playerobjectgroup = playerdata["ObjectGroup"]
        playerelements = playerobjectgroup["Elements"]
        self.player = ObjectGroup(self.WIN, playerobjectgroup["active"], layer=playerdata["Layer"])
        pl = playerelements[0]
        self.player1 = Player(pl["img"], pl["width"],pl["height"],pl["xpos"], pl["ypos"])
        self.player + self.player1 
        self.objdict[self.player.layer].append(self.player)

        # loading a Background from file
        def load_object(file):
            obj_data :dict= Objectloader().load_objdict_from_json(file)
            obj_group = ObjectGroup(self.WIN,obj_data["ObjectGroup"]["active"], layer=obj_data["Layer"])
            for element in obj_data["ObjectGroup"]["Elements"]:
                element: dict
                if element["type"] in self.obj_classes.keys():
                    obj_element = self.obj_classes[element["type"]](element["img"], element["width"], element["height"], element["xpos"], element["ypos"], element["interactive"])
                elif element["type"] == "textbox":
                    obj_element = TextBox(element["text"], element["color"], element["fontsize"], element["width"],element["height"], element["xpos"], element["ypos"], element["fontstyle"])
                elif element["type"] == "itembox":
                    obj_element = ItemBox(self.item_dict[element["item"]], element["fontsize"], element["width"],element["height"], element["xpos"], element["ypos"], element["fontstyle"])
                obj_group + obj_element
            self.objdict[obj_group.layer].append(obj_group)
            return obj_group

        self.hud = load_object(HUD)

        self.stmenu = load_object(SETTINGSMENU)

        self.deathscreengroup = load_object(GAMEOVER)
        
        self.inventorygroup = load_object(INVENTORY)

        self.obstacles = load_object(OBSTACLEJSON)

        self.mainloop()

    def craft(self):
        if self.gold.amount >= 30:
            self.sword + 1
            self.gold - 30
          



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

    def activate_death(self):
        self.deathscreengroup.activate()

    def deactivate_death(self):
        self.deathscreengroup.deactivate()

    def togglehud(self):
        if not self.stmenu.is_active():
            self.activatehelp()
            self.deactivateinventory()
        else:
            self.deactivatehelp()

    def show_deathscreen(self):
        self.deathscreengroup.activate()

    def interact(self):   
        rt:GameObject|None = self.obstacles.interactive_in_range(self.player1)
        if rt is None:
            return
        rt.interact(self.player1, self)
        

    def mainloop(self):

        def get_key_input():

            for event in pg.event.get():      
                if event.type == pg.KEYDOWN:
                    try:
                        self.movementkeys[event.unicode.lower()][0] = True
                        continue
                    except:
                        try:
                            self.overlaykeys[event.unicode.lower()][0]= True
                            continue             
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
            if abs(self.x_move) == abs(self.y_move) == MOVESPEED:
                self.x_move = self.normalized * (self.x_move/abs(self.x_move))
                self.y_move =  self.normalized * (self.y_move/abs(self.y_move))
           
            for  item in self.overlaykeys.values():
                if item[0] and not item[1]:
                    item[2]()
                    item[1] = True
                elif not item[0]:
                    item[1] = False
            
            movement()


        def movement():
            collision = self.obstacles.collision_precheck(self.player1,(self.x_move,self.y_move))
            #collision = self.objdict[OBSTACLE].collision_precheck(self.player1, (self.x_move,self.y_move))  
            focus = self.player1.in_heigh_focus((collision))
            self.player1.move(focus[0])
            #self.backgroud.move(focus[1])
            self.obstacles.move(focus[1])


        def drawing():
            for key in self.objdict_keys:
                for obj in self.objdict[key]:
                    obj.draw()

        def update_items():
            [obj.update_text("") for obj in self.inventorygroup]
            


        while True: 
            self.clock.tick(FPS)
            
            get_key_input()

            if not self.player1.alive:
                self.show_deathscreen()

            handle_input()

            update_items()
            
            self.WIN.fill("black")

            drawing()
           
            display.update()
        

def main():

    Game()


if __name__ == "__main__":
    main()