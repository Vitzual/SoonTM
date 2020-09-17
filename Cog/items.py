import discord
import asyncio
import random
import json
from discord.ext import commands, tasks
from discord.utils import get
from collections.abc import Sequence

class Items(commands.Cog, name="Items"):
    """Items related commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("Moderator")
    @commands.command()
    async def simulate(self, ctx, operation:str):
        
        if operation == "stats":

def setup(bot):
    bot.add_cog(Items(bot))

#################################
########### Get Functions ###########
#################################
# Get functions returns the users current
# specified stat. Usually used in set functions

def get_hp(uuid):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["user_id"] == uuid:
            return scan["current_hp"]
    return -1

def get_max_hp(uuid):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["user_id"] == uuid:
            return scan["max_hp"]
    return -1

def get_mana(uuid):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["user_id"] == uuid:
            return scan["current_mana"]
    return -1

def get_max_mana(uuid):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["user_id"] == uuid:
            return scan["max_mana"]
    return -1

def get_equipped(uuid):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["user_id"] == uuid:
            return scan["equipped"]
    return -1

def get_inventory(uuid):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["user_id"] == uuid:
            return scan["inventory"]
    return -1

#################################
########### Set Functions ###########
#################################
# Set functions, simply put, uses the edit
# function but simplifies the input and
# makes it easier when specifying what
# certain items do during a battle.

def set_hp(uuid, new):
    response = edit(uuid, "current_hp", new)
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #set_death(uuid)
        return True

def add_hp(uuid, new):
    response = edit(uuid, "current_hp", (get_hp(uuid)+new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        return True

def remove_hp(uuid, new):
    response = edit(uuid, "current_hp",  (get_hp(uuid)-new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #set_death(uuid)
        return True

def set_max_hp(uuid, new):
    response = edit(uuid, "max_hp", new)
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #set_death(uuid)
        return True
    
def add_max_hp(uuid, new):
    response = edit(uuid, "max_hp",  (get_max_hp(uuid)+new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        return True
    
def remove_max_hp(uuid, new):
    response = edit(uuid, "max_hp",  (get_max_hp(uuid)-new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #set_death(uuid)
        return True

def set_mana(uuid, new):
    response = edit(uuid, "current_mana", new)
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #mana_empty(uuid)
        return True
    
def add_mana(uuid, new):
    response = edit(uuid, "current_mana",  (get_mana(uuid)+new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        return True
    
def remove_mana(uuid, new):
    response = edit(uuid, "current_mana", (get_mana(uuid)-new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #mana_empty(uuid)
        return True
    
def set_max_mana(uuid, new):
    response = edit(uuid, "max_mana", new)
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #mana_empty(uuid)
        return True
    
def add_max_mana(uuid, new):
    response = edit(uuid, "max_mana", (get_max_mana(uuid)+new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #mana_empty(uuid)
        return True
    
def remove_max_mana(uuid, new):
    response = edit(uuid, "max_mana", (get_max_mana(uuid)-new))
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #mana_empty(uuid)
        return True

#################################
########### Edit Function ###########
#################################
# Edit a users stats. This does not include
# editting a users inventory. For that, use
# the add_item or remove_item functions.
#
# Return values 
# 0 = Invalid
# 1 = Valid
# 2 = Action
#
# If a return value or 0 is sent, that means
# nothing has changed.
#
# If a return value of 1 is sent, that means
# the update to the database went through
#
# If a return value of 2 is sent, that means
# depending on the edit type, tell the calling
# function to take additional action. For
# example no_mana, player_death, etc.

def edit(uuid, a, b):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    index = 0
    for scan in data:
        if scan["user_id"] == uuid:
            if a == "current_hp":
                if b < 0:
                    return 2
                elif b > scan["max_hp"]:
                    b = scan["max_hp"]
                new_data = {
                    "user_id": uuid,
                    "current_hp": b,
                    "max_hp": scan["max_hp"],
                    "current_mana": scan["current_mana"],
                    "max_mana": scan["max_mana"],
                    "equipped": scan["equipped"],
                    "inventory": scan["inventory"]
                }
            elif a == "max_hp":
                if b <= 0:
                    return 0
                elif b < scan["current_hp"]:
                    c = b
                else:
                    c = scan["current_hp"]
                new_data = {
                    "user_id": uuid,
                    "current_hp": c,
                    "max_hp": b,
                    "current_mana": scan["current_mana"],
                    "max_mana": scan["max_mana"],
                    "equipped": scan["equipped"],
                    "inventory": scan["inventory"]
                }
            elif a == "current_mana":
                if b < 0:
                    return 2
                elif b > scan["max_mana"]:
                    b = scan["max_mana"]
                new_data = {
                    "user_id": uuid,
                    "current_hp": scan["current_hp"],
                    "max_hp": scan["max_hp"],
                    "current_mana": b,
                    "max_mana": scan["max_mana"],
                    "equipped": scan["equipped"],
                    "inventory": scan["inventory"]
                }
            elif a == "max_mana":
                if b <= 0:
                    return 0
                elif b < scan["current_mana"],:
                    c = b
                else:
                    c = scan["current_mana"],
                new_data = {
                    "user_id": uuid,
                    "current_hp": scan["current_hp"],
                    "max_hp": scan["max_hp"],
                    "current_mana": c,
                    "max_mana": b,
                    "equipped": scan["equipped"],
                    "inventory": scan["inventory"]
                }
            else:
                return 0
            del data[index]
            data.append(new_data)
            with open(database, "w") as f:
                json.dump(data, f, indent=4)
            return 1
        index+=1
    return 0

#################################
########## Create Function ##########
#################################
# Creates a new index in the database with
# the default stats. Look below in new_data
# for what these stats are set at

def create(uuid):
    database = "Axiiom/user_inventory.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["user_id"] == uuid:
            return False
    new_data = {
        "user_id": uuid,
        "current_hp": 10,
        "max_hp": 10,
        "current_mana": 10,
        "max_mana": 10,
        "equipped": [],
        "inventory": []
    }
    data.append(new_data)
    with open(database, "w") as f:
        json.dump(data, f, indent=4)
    return True