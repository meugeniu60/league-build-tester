import pandas as pd
from Helper import to_float

class Ability(object):
    
    def __init__(self, name:str,desc_obj,  **extra):
        self.name = name
        
        self.extra = extra
        self.cd_type = "static"
        if hasattr(self.extra,"RECHARGE"):
            self.cd_type = "recharge"
        elif "PER SECOND" in self.extra.get("COST",''):
            self.cd_type = "toggle"
            
        self.description = desc_obj
        
    
    