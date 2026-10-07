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

        self.current_version = "V0"
    
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

    def load_champ(self, champ_name:str):

        champ_name = champ_name.title()

        self.get(BASE_SITE+champ_name)
        
        # Get Available version
        version_node = self.find_element("xpath", "//div[@class='infobox-data-label' and text()='Last changed']")
        version_node = version_node.find_element("xpath", "./..")
        version_node = version_node.find_element("xpath", "./descendant::a")
        self.current_version = version_node.text
        saved_version = Saves.get_champ_save_ver(champ_name)
        
        if saved_version and Saves.compare_version(saved_version, self.current_version) < 0:
            self.champ = Saves.load_champ(champ_name, saved_version)
        else:
            self.scrape_champ(champ_name=champ_name)
    
    def scrape_champ(self, champ_name:str) -> Champion:
        
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
        # Stats Got
        
        # Get abilities
        abilities = list()
        abil_containers = self.find_elements("class name", "skill_header")
        for container in abil_containers:
            container = container.find_element("class name", "ability-info-container")
            wrapper = container.find_element("class name", "ability-info-stats__wrapper")
            titlecard = wrapper.find_element("class name", "ability-info-stats__ability")
            additional_info = wrapper.find_element("class name", "ability-info-stats__list")
            name = titlecard.text
            text = container.text
            
            if flavor := container.find_element("class name", "ability-info-flavor"):
                text = text.removesuffix(flavor.text)
            text += "\n" + additional_info.text
            # extra_windows = wrapper.find_elements("xpath", "./div[@class='ability-info-stats__list']/div")
            # extra = dict()
            # for window in extra_windows:
            #     extra[window.find_element("class name", "ability-info-stats__stat-label").text.strip(":.;")] = clean_stat(window.find_element("class name", "ability-info-stats__stat-value").text)
            
            # container = container.find_element("class name", "ability-info-content")
                
            # effects = list()
            # effect_windows = container.find_elements("class name", "ability-info-row")
            # for window in effect_windows:
            #     effect = dict()
            #     effect["description"] = window.find_element("class name", "ability-info-description").text
                
            #     spec_windows = window.find_elements("class name", "ability-info-stats")
            #     if spec_windows:
            #         specs = dict()
            #         spec_windows = spec_windows[0].find_elements("class name", "skill-tabs")
            #         for window in spec_windows:
            #             title = window.find_element("xpath", ".//span[@class='template_lc']").text
            #             desc = window.text.removeprefix(title).strip(" \n►")
            #             specs[title] = clean_stat(desc)
            #         effect["specs"] = specs
                
            #     effects.append(effect)
            
            # abilities.append(Ability(name, effects, **extra))
            abilities.append({
                "name": name,
                "text": text
            })
        # Abilities Got

        champ_obj = stats
        champ_obj["abilities"] = abilities
        self.champ = champ_obj
        
        # Save champ
        Saves.save_champ(champ_obj)
                
    
    def scrape_item(self, item:str):
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
        stats["name"] = it_name

        
        passive_abilities = list()
        passive_index = index("Passive")
        if passive_index != -1:
            node_passive = section[passive_index + 1]
            for div in node_passive.find_elements("class name", "infobox-data-row"):
                div = div.find_element("class name", "infobox-data-value")
                passive_abilities.append(div.text)
        

        active_index = index("Active")
        if active_index != -1:
            node_active = section[active_index + 1]
            for div in node_active.find_elements("class name", "infobox-data-row"):
                div = div.find_element("class name", "infobox-data-value")
                active_ability = div.text

                
        recipe_index = index("Recipe")
        div_cost = section[recipe_index + 1]
        if div_cost.get_attribute("class") != "infobox-section-cell":
            div_components = div_cost
            div_cost = section[recipe_index + 2]
            
            # Get components
            recipe = list()
            for div in div_components.find_elements("xpath", ".//a"):
                recipe.append(div.get_attribute("href").removeprefix("https://wiki.leagueoflegends.com/en-us/"))
                
            recipe.remove('gold')
            recipe.append(div_components.text.strip(" +%"))
            stats["Recipe"] = recipe
        
        # Get total cost/sell
        for div in div_cost.find_elements("class name", "infobox-data-row"):
            lable = div.find_element("class name", "infobox-data-label").text
            if lable not in ["cost", "sell"]:
                continue
            stats[lable] = div.find_element("class name", "infobox-data-value").text
        item_dict = stats
        if active_ability:
            item_dict["active"] = active_ability
        if passive_abilities:
            item_dict["passives"] = passive_abilities
        return item_dict
    
    #Item(passive=passive_abilities, active=active_ability, **stats)
        
    
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
            items += [self.scrape_item(item_link)]
        

# def clean_stat(stat:str|list) -> dict:
#     """_summary_

#     Args:
#         stat (str | list): string like "10 / 50 / 200 / 250 (+ 15% bonus ad)(+ 30% ap) magic damage" or same string .split()

#     Returns:
#         (cleaned stat)
#         dict:   base:       list(10, 50, 200, 250)
#                 text:       "magic damage"
#                 is_procent  (bool)
#                 scaling     list(cleaned_stat("15% bonus ad"), cleaned_stat("30% ap"))
         
#     """
#     if isinstance(stat, str):
#         splited = stat.split()
#     else:
#         splited = stat
        
#     # Result values
#     base = list()
#     text = ""
#     scaling = list()
#     is_procent = False
    
#     i = 0
#     slen = len(splited)
#     stage_state = True
#     while i < slen:
#         if stage_state:
#             if splited[i].endswith("%"):
#                 is_procent = True
#                 splited[i] = splited[i].strip("%")
                
#             base.append(float(splited[i]))
#             stage_state = False
        
#         elif splited[i] in '/–':
#             stage_state = True
            
#         elif splited[i] == 'per':
#             i += 1
#             b = float(splited[i].strip("%."))
#             base = [num / b for num in base]
            
#         elif splited[i] == '(+':
#             i += 1
#             j = slen - 1
            
#             while not splited[j].endswith(')'):
#                 j -= 1
#             splited[j] = splited[j].removesuffix(')')
#             scaling.append(clean_stat(splited[i:j+1]))
#             i = j
#         else:
#             text += splited[i]+" "
#         i += 1
    
#     return dict(base=base, text=text, scaling=scaling, is_procent=is_procent)
  
        
# Testing part  


import os
# if os.path.exists("Saves\\Champs\\Aatrox_V25.12.json"):
#     os.remove("Saves\\Champs\\Aatrox_V25.12.json")
sc = Scraper()
# sc.load_champ("Aatrox")
sc.load_champ("Jinx")
print(sc.champ.abil)
# file_path = "log.json"
# if os.path.exists(file_path):
#     os.remove(file_path)
    
# with open(file_path, 'xs') as file:
#     file.write(json.dump(sc.champ,indent=4))
        
sc.update_items("Legendary items")
