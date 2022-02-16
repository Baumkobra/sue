
from multiplayer import * 
import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600)) # change to the real resolution
class T:
    def inventory(self) -> None:
        self.inventorygroup = ObjectGroup(None,False,TOP)
        self.inventorygroup + ItemBox(Gold(0),40,50,50,
                220.0,
                190.0, active=True)
        self.inventorygroup + ItemBox(Silber(0),40,50,50,
                220.0,
                220.0, active= True)
        self.inventorygroup + ItemBox(Sword(0),40,50,50,
                220.0,
                250, active= False)
        with open(INVENTORY, "w") as file:
            json.dump(self.inventorygroup.to_dict(), file, indent = 4)
        print(self.inventorygroup.to_dict())
        
#T().inventory()


exec("x = T()")
print(x.inventory())
