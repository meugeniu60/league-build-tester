from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
import time

from Champion import Champion
from ChampAbility import Ability

PAGE_LOAD = 0.4
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
            self.browser.find_element(by=by, value=value)
        else:
            self.browser.find_element(value=value)

    def read_ability(self, text) -> Ability:
        pass

    def load_champ(self, champ_name:str) -> Champion:
        # add check version later
        
        self.get(BASE_SITE+champ_name)
        
        stats = dict()
        for statName, details in self.stat_map.items():
            base = None
            inc = None
            
            if "Default" in details["getType"]:
                node = self.browser.find_element(value=details["span_id"])
                text = node.text
                
                if "Single" not in details["getType"]:
                    splits = text.split(" – ")
                    base = int(splits[0])
                    cap = int(splits[-1])
                    inc = (cap - base) /17
                else:
                    base = int(text)

                time.sleep(3)
                
        
        
sc = Scraper()
sc.load_champ("Ahri")

        

