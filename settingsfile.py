HOST, PORT = "127.0.0.1", 50000
MOVESPEED = 9
MAP = "map.json"
PLAYER = "data//player.json"
GAMEOVER = "data//gameoverscreen.json"
HFORHELP = "data//hforhelp.json"
HUD = "data//hud.json"
INVENTORY = "data//inventory.json"
OBSTACLEJSON = "data//obstacles.json"
SETTINGSMENU = "data//settingsmenu.json"
WIDTH = 1000
HEIGHT = 1000
FLIPPEDLEFT = -1
FLIPPEDRIGHT = 1
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
GOLD = (218,165,32)
SILBER = (192,192,192)
RED = (255,0,0)




from math import sqrt


print(MOVESPEED/sqrt(2))