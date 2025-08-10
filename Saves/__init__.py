import json
import os
import pickle
from Champion import Champion

VER_BASE = 100
CLEAN_OLD_VERSIONS = True
CHAMPION_FOLDER = "Champs"
ITEMS_FOLDER = "Items"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

def champ_file_from_version(name:str, ver:str="V0"):
    return os.path.join(THIS_FOLDER, CHAMPION_FOLDER, f"{name}_{ver}.json")

def version_from_file_name(file:str):
    ver = file.split("_")[-1]
    ver = ver.removesuffix(".json")
    return ver


def compare_version(ver1:str, ver2:str):
    """compares 2 version strings

    Args:
        ver1 (str): first version
        ver2 (str): second version
    Returns:
        0 for ver2 = ver1
        <0 if ver2 < ver1
        >0 if ver2 > ver1
    """
    
    def split_ver(ver:str) -> list:
        s = ver.split(".")
        for i in range(len(s)):
            s[i] = int(s[i].strip("Vv"))
        return s
    
    v1 = split_ver(ver1)
    v2 = split_ver(ver2)
    version_delta = 0
    while v1 or v2:
        i1 = 0
        i2 = 0
        if v1:
            i1 = v1.pop(0)
        if v2:
            i2 = v2.pop(0)
        version_delta += i2-i1
        version_delta *= VER_BASE
    
    return version_delta


def search_dir(starting_directory, string_to_search):
    directory_list = []
    for directory in [x[0] for x in os.walk(starting_directory)]:
        if string_to_search in os.path.basename(os.path.normpath(directory)):
            directory_list.append(directory)
    return directory_list        


def get_champ_save_ver(name:str):
    champ_files = search_dir(CHAMPION_FOLDER, name)
    
    if not champ_files:
        return False
    
    saved_versions = list()
    for file in champ_files:
        file_ver = version_from_file_name(file)
        i = 0
        while i<len(saved_versions):
            if compare_version(saved_versions[i], file_ver) >0:
                break
            else:
                i += 1
        saved_versions.insert(i, file_ver)
        
    if CLEAN_OLD_VERSIONS:
        for i in range(1, len(saved_versions)):
            os.remove(champ_file_from_version(name=name, ver=saved_versions[i]))
    
    return  saved_versions[0]

def save_champ(champ:Champion):
    file_path = champ_file_from_version(champ.name, champ.version)
    if os.path.exists(file_path):
        os.remove(file_path)
    # TODO make serializer
    with open(file_path, 'xb') as file:
        pickle.dump(champ, file)
    
def load_champ(champ_name:str, ver:str):
    with open(champ_file_from_version(champ_name, ver), 'rb') as file:
        return Champion(pickle.load(file))
