# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options

# import json
# import time

# import Saves
# from Champion import Champion
# from ChampAbility import Ability


# BASE_SITE = "https://wiki.leagueoflegends.com/en-us/"
# TEST_CHAMP = "Amumu"

# self = webdriver.Firefox(Options().binary_location)
# self.get(BASE_SITE+TEST_CHAMP)

# def clean_stat(stat:str|list) -> dict:
#     if isinstance(stat, str):
#         splited = stat.split()
#     else:
#         splited = stat
        
#     # Result values
#     base = list()
#     text = ""
#     stages = 1
#     scaling = list()
    
#     in_stages = True
#     finished = False
    
#     i = 0
#     while not finished:
#         if in_stages:
#             base.append(float(splited[i].strip('%')))
#             in_stages = False
        
#         elif splited[i] == '/':
#             in_stages = True
#             stages += 1
        
#         elif splited[i] == '(+':
#             i += 1
#             j = i
#             while not splited[i].endswith(')'):
#                 i += 1
#             splited[i] = splited[i].removesuffix(')')
#             scaling.append(clean_stat(splited[j:i+1]))
        
#         else:
#             text += splited[i] + ' '
            
#         if i == len(splited) - 1:
#             finished = True
            
#         i += 1
    
#     return dict(base=base, text=text, stages=stages, scaling=scaling)
    

# abil_containers = self.find_elements("class name", "skill_header")
# for container in abil_containers:
#     container = container.find_element("class name", "ability-info-container")
    
#     wrapper = container.find_element("class name", "ability-info-stats__wrapper")
#     name = wrapper.text
    
#     extra_windows = wrapper.find_elements("xpath", "./div[@class='ability-info-stats__list']/div")
#     extra = dict()
#     for window in extra_windows:
#         extra[window.find_element("class name", "ability-info-stats__stat-label").text] = clean_stat(window.find_element("class name", "ability-info-stats__stat-value").text)
    
#     container = container.find_element("class name", "ability-info-content")
        
#     effects = list()
#     effect_windows = container.find_elements("class name", "ability-info-row")
#     for window in effect_windows:
#         effect = dict()
#         effect["description"] = window.find_element("class name", "ability-info-description").text
        
#         spec_windows = window.find_elements("class name", "ability-info-stats")
#         if spec_windows:
#             specs = dict()
#             spec_windows = spec_windows[0].find_elements("class name", "skill-tabs")
#             for window in spec_windows:
#                 title = window.find_element("xpath", ".//span[@class='template_lc']").text
#                 desc = window.text.removeprefix(title)
#                 specs[title] = clean_stat(desc)
#             effect["specs"] = specs
        
#         effects.append(effect)
import re
class Ability(object):
    
    def __init__(self, name:str,desc_obj,  **extra):
        self.name = name
        
        self.description = desc_obj
        if isinstance(self.description ,list):
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
        
class TestObj(object):
    def __init__(self):
        self.name = "Aatrox"
        self.version = "v5.3"
        self.abilities = [Ability("giga beam","user gets 50 ability power")]
    
    def do_damage(self):
        return 50
import pickle, os
def save(obj, file, open_setting = 'xb'):
    if os.path.exists(file) and 'x' in open_setting:
        os.remove(file)
    with open(file, open_setting) as _file:
        pickle.dump(obj, _file)

def load(file, open_setting = 'rb'):
    with open(file, open_setting) as _file:
        return pickle.load(_file)

t = [TestObj(), TestObj(), TestObj()]
save(t,"test.pkl", 'wb')
save(t,"test.pkl", 'ab')
# save(t,"test.pkl", 'ab')
r = load("test.pkl")
print(r[0].name)


