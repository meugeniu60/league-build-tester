from ChampAbility import Ability

import pandas as pd

class Champion(object):
    def __init__(self, name:str, version:str="V0"):
        self.name = name
        self.version = version
    
    def update_stats(self, stats:dict):
        if not hasattr(self, "stats"):
            self.stats = stats
        else:
            for key, val in stats.items():
                self.stats[key] = val
    
    def update_abilities(self, abilities:list):
        self.abil = abilities
    
    