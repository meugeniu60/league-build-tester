from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
import time

import Saves
from Champion import Champion
from ChampAbility import Ability
from Item import Item

PAGE_LOAD = 0.5
FIND_ELEMENT = 0.2
BASE_SITE = "https://wiki.leagueoflegends.com/en-us/"


def is_float(s:str):
    return s.replace(".","", 1).isnumeric()

def clean_stat(stat:str|list) -> dict:
    if isinstance(stat, str):
        splited = stat.split()
    else:
        splited = stat
        
    # Result values
    base = list()
    text = ""
    stages = 1
    scaling = list()
    is_procent = False
    
    i = 0
    finished = False
    in_stages = is_float(splited[i])

    while not finished:
        if i == len(splited) - 1:
            finished = True
        elif i >= len(splited):
            break
        
        if in_stages:
            if splited[i].endswith("%"):
                is_procent = True
                splited[i] = splited[i][:-1]
                
            while i<len(splited) and not is_float(splited[i]):
                i += 1
                
            base.append(float(splited[i]))
            in_stages = False
        
        elif splited[i] in '/–':
            in_stages = True
            stages += 1
        
        elif splited[i] == '(+':
            i += 1
            j = i
            while not splited[i].endswith(')'):
                i += 1
            splited[i] = splited[i].removesuffix(')')
            scaling.append(clean_stat(splited[j:i+1]))
        
        else:
            text += splited[i] + ' '
            
        i += 1
    
    return dict(base=base, text=text, stages=stages, scaling=scaling, is_procent=is_procent)

class Scraper:
    """Opens browser
        get_champion = 
        if no file 
            create file 
        else if champ needs update
            update file
        read file keep info   
    """
    def __init__(self):
        #initialize browser
        self.browser = webdriver.Firefox(Options().binary_location)
        self.get(BASE_SITE)
        with open("StatsMap.json", "r") as file:
            self.stat_map = json.load(file)
    
    def get(self, site:str = None):
        """Changes page to site
        If page is not a website it will enter BASE_SITE, looking for a page titled *site*

        Args:
            site (str, optional): Site or page you want to access. Defaults to None.
        """
        if not site.startswith("http"):
            self.browser.get(BASE_SITE+site.removeprefix(r"/en-us/"))
        else:
            self.browser.get(site)
        time.sleep(PAGE_LOAD)

    def find_element(self, by = None, value:str = None):
        if by!=None:
            result = self.browser.find_element(by=by, value=value)
        else:
            result = self.browser.find_element(value=value)
        time.sleep(FIND_ELEMENT)
        return result
    
    def find_elements(self, by = None, value:str = None):
        if by!=None:
            result = self.browser.find_elements(by=by, value=value)
        else:
            result = self.browser.find_elements(value=value)
        time.sleep(FIND_ELEMENT)
        return result

    def read_ability(self, text) -> Ability:
        pass
    
    def load_champ(self, champ_name:str) -> Champion:

        champ_name = champ_name.title()

        self.get(BASE_SITE+champ_name)
        
        # Get Available version
        version_node = self.find_element("xpath", "//div[@class='infobox-data-label' and text()='Last changed']")
        version_node = version_node.find_element("xpath", "./..")
        version_node = version_node.find_element("xpath", "./descendant::a")
        current_version = version_node.text
        saved_version = Saves.get_champ_save_ver(champ_name)
        
        if saved_version and Saves.compare_version(saved_version, current_version) < 0:
            self.champ = Saves.load_champ(champ_name, saved_version)
        else:
            # Scrape Champ
            champ_obj = Champion(name=champ_name, version=current_version)
            
            # Get Stats
            stats = dict()
            for statName, details in self.stat_map.items():
                def parseStat(tail):
                    base = None
                    inc = None
                    
                    def singleSplit(text:str):
                        text = text.replace("%","")
                        inc = None
                        if "Single" not in tail["getType"]:
                            splits = text.split(" ")
                            base = float(splits[0])
                            cap = float(splits[-1])
                            inc = (cap - base) /17
                        else:
                            if "N/A" in text:
                                base = None
                            else:
                                base = float(text)
                        return base, inc
                    
                    if "Default" in tail["getType"]:
                        try:
                            node = self.find_element(by="xpath",value= f"//span[@id='{tail["span_id"]}']")
                            text = node.text
                            base, inc = singleSplit(text)
                        except:
                            base, inc = None, None
                            
                    elif "ByLable" in tail["getType"]:
                        node = self.find_element(by= "xpath", value= f"//a[@title='{tail["title"]}' and text()='{tail["text"]}']")
                        node = node.find_element(by="xpath", value=r"./../..")
                        # node = node.find_element(by="xpath", value=r"./../..")
                        node = node.find_element(by="xpath", value=f"./div[@class='infobox-data-value statsbox']")
                        text = node.text
                        base, inc = singleSplit(text)
                    
                    elif "Split" in tail["getType"]:
                        base, _ = parseStat(tail=tail["Base"])
                        _, inc = parseStat(tail=tail["Inc"])
                    
                    elif "ToolTip" in tail["getType"]:
                        node = self.find_element(by="xpath", value=f"//span[@class='glossary tooltips-init-complete' and @data-tip='{tail["data-tip"]}']/../../div[@class='infobox-data-value statsbox']")
                        text = node.text
                        base, inc = singleSplit(text)
                        
                    elif "None" in tail["getType"]:
                        base = tail["default"]
                        
                    return base, inc
                
                base, inc = parseStat(details)
                stats[statName] = {"Base":base}
                if inc:
                    stats[statName]["Inc"] = inc       
            champ_obj.update_stats(stats)
            # Stats Got
            
            # Get abilities
            abilities = list()
            abil_containers = self.find_elements("class name", "skill_header")
            for container in abil_containers:
                container = container.find_element("class name", "ability-info-container")
                
                wrapper = container.find_element("class name", "ability-info-stats__wrapper")
                name = wrapper.text
                
                extra_windows = wrapper.find_elements("xpath", "./div[@class='ability-info-stats__list']/div")
                extra = dict()
                for window in extra_windows:
                    extra[window.find_element("class name", "ability-info-stats__stat-label").text] = clean_stat(window.find_element("class name", "ability-info-stats__stat-value").text)
                
                container = container.find_element("class name", "ability-info-content")
                    
                effects = list()
                effect_windows = container.find_elements("class name", "ability-info-row")
                for window in effect_windows:
                    effect = dict()
                    effect["description"] = window.find_element("class name", "ability-info-description").text
                    
                    spec_windows = window.find_elements("class name", "ability-info-stats")
                    if spec_windows:
                        specs = dict()
                        spec_windows = spec_windows[0].find_elements("class name", "skill-tabs")
                        for window in spec_windows:
                            title = window.find_element("xpath", ".//span[@class='template_lc']").text
                            desc = window.text.removeprefix(title).strip(" \n►")
                            specs[title] = clean_stat(desc)
                        effect["specs"] = specs
                    
                    effects.append(effect)
                
                abilities.append(Ability(name, effects, **extra))
                
            champ_obj.update_abilities(abilities)
            # Abilities Got
            
            self.champ = champ_obj
            
            # Save champ
            Saves.save_champ(champ_obj)
                
    
    def load_item(self, item:str):
        self.get(item)
        
        it_name = item.removeprefix("https://wiki.leagueoflegends.com/en-us/")
        infobox = self.find_element("class name", "infobox")
        # header = infobox.find_elements("xpath", "./div[contains(@class, header)]")
        section = infobox.find_elements("xpath", "./div")
        
        def index(title:str) -> int:
            try:
                head = infobox.find_element("xpath", f'./div[contains(@class, "header") and text()="{title}"]')
                return section.index(head)
            except:
                return -1
        
        node_stats = section[index("Stats")+1]
        stats = dict()
        for div in node_stats.find_elements("xpath", './/div[@class="infobox-data-row"]'):
            div = div.find_element("class name", "infobox-data-value")
            if not div.text:
                continue
            num, *stat = div.text.split()
            if num[-1].isdigit():
                num = int(num.strip('+%'))
                
                stat = " ".join(stat)
                stats[stat] = num
            else:
                stats["gold per 10 seconds"] = float(stat[1])
        stats["Name"] = it_name
        
        passive_abilities = list()
        passive_index = index("Passive")
        if passive_index != -1:
            node_passive = section[passive_index + 1]
            for div in node_passive.find_elements("class name", "infobox-data-row"):
                div = div.find_element("class name", "infobox-data-value")
                passive_abilities.append(div.text)
        
        active_abilities = list()
        active_index = index("Active")
        if active_index != -1:
            node_active = section[active_index + 1]
            for div in node_active.find_elements("class name", "infobox-data-row"):
                div = div.find_element("class name", "infobox-data-value")
                active_abilities.append(div.text)
                
        recipe_index = index("Recipe")
        div_cost = section[recipe_index + 1]
        if div_cost.get_attribute("class") != "infobox-section-cell":
            div_components = div_cost
            div_cost = section[recipe_index + 2]
            
            # Get components
            recipe = list()
            for div in div_components.find_elements("xpath", ".//a"):
                recipe.append(div.get_attribute("href").removeprefix("https://wiki.leagueoflegends.com/en-us/"))
                
            recipe.remove('Gold')
            recipe.append(div_components.text.strip(" +%"))
            stats["Recipe"] = recipe
        
        # Get total cost/sell
        for div in div_cost.find_elements("class name", "infobox-data-row"):
            lable = div.find_element("class name", "infobox-data-label").text
            if lable not in ["Cost", "Sell"]:
                continue
            stats[lable] = div.find_element("class name", "infobox-data-value").text
        
        return Item(passive=passive_abilities, active=active_abilities, **stats)
        
    
    def update_items(self, name):
        # Collect names
        d_items = dict()
        self.get("Item#List_of_Items")
        
        # Get grid
        grid = self.find_element("id", "item-grid")
        grid = grid.find_element("id", "grid")
        grid = grid.find_element("id", "item-grid")
        
        titles = grid.find_elements("xpath", "./dl")
        it_list = grid.find_elements("xpath", "./div[@class='tlist']")
        for i in range(len(titles)):
            it_type = titles[i].text
            if it_type != name:
                continue
            d_items[it_type] = list()
            
            it_links = it_list[i].find_elements("xpath", ".//a")
            for it_link in it_links:
                d_items[it_type].append(it_link.get_attribute("href"))
                
        # Get items
        items = []
        for item_link in d_items[name]:
            items += [self.load_item(item_link)]
        
        
        
            


import os
# if os.path.exists("Saves\\Champs\\Aatrox_V25.12.json"):
#     os.remove("Saves\\Champs\\Aatrox_V25.12.json")
sc = Scraper()
# sc.load_champ("Aatrox")
# sc.load_champ("Aatrox")

# file_path = "log.json"
# if os.path.exists(file_path):
#     os.remove(file_path)
    
# with open(file_path, 'xs') as file:
#     file.write(json.dump(sc.champ,indent=4))
        
sc.update_items("Legendary items")
