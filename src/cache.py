"""Caches the results from the API."""
import time
import threading
import json
import os

CHAMPIONS_CACHE_TIME = 604800L #Cache champions names for 1 week max
CHAMPIONS_LOCK = threading.Lock()
CHAMPIONS_FILE = os.path.dirname(os.path.abspath(__file__)) + "\\..\\cache\\champions.json"

def load_from_file():
    """Loads the stored champions from file"""
    try:
        with open(CHAMPIONS_FILE, "r") as myfile:
            data = myfile.read()
            return json.loads(data)
    except IOError:
        return {}
    except ValueError:
        return {}

CHAMPIONS = load_from_file()

def champion_name_available(champion_id):
    """Checks if a champion is available in cache and fresh"""
    if str(champion_id) not in CHAMPIONS:
        return False

    storetime = CHAMPIONS[str(champion_id)]["time"]
    if storetime + CHAMPIONS_CACHE_TIME < curr_time_long():
        return False

    return True

def get_champion_name(champion_id):
    """Returns the champion name from cache"""
    if not champion_name_available(champion_id):
        return ""

    return CHAMPIONS[str(champion_id)]["name"]

def add_champion_name(champion_id, champion_name):
    """Adds a new champion to the cache"""
    with CHAMPIONS_LOCK:
        if champion_name_available(champion_id):
            CHAMPIONS[str(champion_id)]["time"] = curr_time_long()
        else:
            CHAMPIONS[str(champion_id)] = {"name" : champion_name, "time" : curr_time_long()}
        json.dump(CHAMPIONS, open(CHAMPIONS_FILE, "w"))

def curr_time_long():
    """Returns current time without decimal part"""
    return long(time.time())
