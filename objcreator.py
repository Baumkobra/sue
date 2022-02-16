
from multiplayer import * 
class T:
    def inventory(self) -> None:
        self.inventorygroup = ObjectGroup(self.WIN,False,TOP)
        self.inventorygroup + GameObject("data/gray 80.png",400,400,200,400,active = True, interactive=False)
        print(GameObject("data/black.png",400,400,200,400).to_dict())
        self.inventorygroup + ItemBox(Gold(0),40,50,50,
                220.0,
                190.0, active=True)
        self.inventorygroup + ItemBox(Silber(0),40,50,50,
                220.0,
                 active= True)
        self.inventorygroup + ItemBox(Sword(0),40,50,50,
                220.0,
                190.0, active= False)
        with open(INVENTORY, "w") as file:
            json.dump(self.inventorygroup.to_dict(), file, indent = 4)
        print(self.inventorygroup.to_dict())
T().inventory()
