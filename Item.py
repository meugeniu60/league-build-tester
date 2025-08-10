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
        
    def add_ability(self,abil:IAbility|list, reset=False):
        is_list = isinstance(abil, list)
        if reset:
            if is_list:
                self.abili = abil
            else:
                self.abili = [abil]
            return
        
        if is_list:
            self.abili.extend(abil)
        else:
            self.abili.append(abil)
    
    def __init__(self, abil:IAbility|list=None, **stats):
        self.add_stats(reset=True, **stats)
        self.add_ability(reset=True, abil=abil)