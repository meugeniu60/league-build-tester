from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
import time

from Champion import Champion
from ChampAbility import Ability

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
    
    def get(self, site:str):
        if not site.startswith("http"):
            print(f"{site} is not a website")
            return        
        self.browser.get(site)
        time.sleep(PAGE_LOAD)

    def find_element(self, by = None, value:str = None):
        if by!=None:
            result = self.browser.find_element(by=by, value=value)
        else:
            result = self.browser.find_element(value=value)
        time.sleep(FIND_ELEMENT)
        return result

    def read_ability(self, text) -> Ability:
        pass
    
    def load_champ(self, champ_name:str) -> Champion:
        # add check version later
        champ_name = champ_name.title()
        self.get(BASE_SITE+champ_name)
        
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
        
        pass
                
        
        
sc = Scraper()
sc.load_champ("Aatrox")

        

