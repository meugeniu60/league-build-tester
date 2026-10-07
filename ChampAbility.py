import re
from Helper import to_float

class Ability(object):
    
    def __init__(self, name:str,desc_obj,  **extra):
        self.name = name
        
        self.description = ""
        if isinstance(desc_obj, list):
            # champion ability from scraper
            # desc_obj:     list[dict["description"]:   text   
            #                        ["specs"]:         dict[title]:cleaned stat]
            # extra:        dict[title]:    cleaned stat
            # cleaned stat is in scraper
            self.extra = extra
            self.cd_type = "static"
            if x := self.extra.get("RECHARGE", None):
                self.cd_type = "recharge"
                self.recharge = x
            elif "PER SECOND" in self.extra.get("COST",''):
                self.cd_type = "toggle"
            elif not extra.get("STATIC COOLDOWN", None):
                self.cd_type = "passive"
            else:
                self.cd_type = "static"

        else:
            # Simple abil
            cd_match = re.match("(\\d*)\\ssecond(|s)\\scooldown", desc_obj)
            if cd_match:
                self.cd_type = "static"
                self.cooldown = cd_match.groups()[0]
            else:
                self.cd_type = "passive"
            self.description = desc_obj
                
                
        
    
    