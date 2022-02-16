from settingsfile import *
from random import randint
import json
TILESIZE = 250
dc = {"Layer":"MIDDLE", "ObjectGroup":{
    "active":True,
    "Elements":[]}}
for x in range(-5000,5000,TILESIZE):
    for y in range(-5000,5000,TILESIZE):
        r = randint(0,30)
        if  r == 0:
            data = {"type": "default", "img": "data//blue.png", "width":TILESIZE,"height":TILESIZE,"xpos":x, "ypos":y, "interactive":False}
        elif r == 1:
            continue
            data = {"type": "destructible", "img": "data//green.png", "width":TILESIZE,"height":TILESIZE,"xpos":x, "ypos":y, "interactive":True}
        elif r == 2:
            data = {"type": "killable", "img": "data//red.png", "width":TILESIZE,"height":TILESIZE, "xpos":x, "ypos":y,"interactive":True}
        elif r == 3:
            data = {"type": "goldore", "img": "data//green.png", "width":TILESIZE,"height":TILESIZE, "xpos":x, "ypos":y,"interactive":True}
        elif r == 4:
            data = {"type": "silberore", "img": "data//green.png", "width":TILESIZE,"height":TILESIZE, "xpos":x, "ypos":y,"interactive":True}

        else:
            continue
        dc["ObjectGroup"]["Elements"].append(data)

with open("data//obstacles.json", "w") as file:
    json.dump(dc,file, indent=4)

