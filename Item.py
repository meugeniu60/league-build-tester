class IAbility(object):
    def __init__(self, desc:str):
        self.description = desc

class Item(object):
    def add_stats(self, reset=False, **stats):
        if reset:
            self.stats = stats
            return
        
        for key, value in stats.items:
            self.stats[key] = value
        
    def add_ability(self, passive:IAbility|str|list=None, active:IAbility|str|list=None):
        if not passive and not active:
            return -1
        def refine_abil(abil):
            if not isinstance(abil, list):
                abil = [abil]
            return list(map(lambda x: x if(isinstance(x, IAbility)) else IAbility(x), abil))
        
        if active:
            active = refine_abil(active)
            self.active = active[-1]
        if passive:
            passive = refine_abil(passive)
            self.passive = passive
    
    def __init__(self, passive:IAbility|str|list=None, active:IAbility|str|list=None, **stats):
        self.name = stats.pop("Name")
        self.cost = stats.pop("Cost")
        self.sell = stats.pop("Sell")
        self.recipe = stats.pop("Recipe", None)
        
        self.add_stats(reset=True, **stats)
        self.add_ability(passive=passive, active=active)