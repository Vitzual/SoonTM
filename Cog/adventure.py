import discord
import asyncio
import random
import json
import math
from discord.ext import commands, tasks
from discord.utils import get
from collections.abc import Sequence
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class Adventure(commands.Cog, name="Adventure"):
    """Adventure related commands"""
    def __init__(self, bot):
        self.bot = bot
        
    @commands.has_role("Moderator")
    @commands.command()
    async def convert(self, ctx, operation:str, XP:int=0):
        if operation.lower() == "xp":
            level = int(0.16 * math.sqrt(XP))
            await ctx.send(f"{XP}xp translates to level {level}")
        elif operation.lower() == "level":
            xpp = int(math.pow((XP/0.16),2))
            await ctx.send(f"Level {XP} translates to {xpp}xp")
        elif operation.lower() == "graph":
            message,index,current,accumulated = "",0,0,0
            while index != 61:
                XP = int(math.pow((index/0.12),2))
                XP = int(math.ceil(XP / 100.0)) * 100
                accumulated = accumulated + (XP-current)
                message = message + f"Level {index} | {XP-current}xp\n"
                current = XP
                index+=1
            message=message+f"\n{accumulated}xp total"
            await ctx.send(message)
        elif operation.lower() == "simulation":
            accumulated,simulation,index = 250000,0,0
            while simulation < accumulated:
                generate = random.randint(50,150)
                if generate in [50,51,52,53,54,55]:
                    generate = 0
                while generate > 0:
                    simulation = simulation + (random.randint(5,10))
                    generate-=1
                index+=1
            await ctx.send(f"Simulation took {index} days!")

    @commands.has_role("Moderator")
    @commands.command()
    async def simulate(self, ctx, operation:str, variable:int=0):
        user = ctx.author
        if operation == "create":
            valid = create(user)
        elif operation == "stats":
            await ctx.send(embed=display_stats(user))
        elif operation == "damage":
            response = remove_hp(user.id, variable)
        elif operation == "heal":
            response = add_hp(user.id, variable)

    @commands.has_role("Moderator")
    @commands.command()
    async def create(self, ctx, operation:str):
        def check(m):
            return m.author == user
        if operation.lower() == "item":
            user,effects = ctx.author,[]
            await ctx.send(embed=prompt_name())
            name = await self.bot.wait_for('message', check=check)
            if check_name(name.content.lower()) is False:
                await ctx.send(embed=invalid_name(name.content))
                return
            await ctx.send(embed=prompt_description(name.content))
            description = await self.bot.wait_for('message', check=check)
            await ctx.send(embed=prompt_link(name.content))
            link = await self.bot.wait_for('message', check=check)
            if check_link(link.content) is False:
                await ctx.send(embed=invalid_type(link.content))
                return
            await ctx.send(embed=prompt_item(name.content))
            item = await self.bot.wait_for('message', check=check)
            if not check_type(item.content.lower()):
                await ctx.send(embed=invalid_type(item.content))
                return
            embed, effect = prompt_variable(item.content.lower())
            if embed is not None:
                await ctx.send(embed=embed)
                variable = await self.bot.wait_for('message', check=check)
                if not check_variable(int(variable.content), item.content.lower()):
                    await ctx.send(embed=invalid_type(variable.content))
                    return
            else:
                variable = 0
            if effect is True:
                while effect is not False:
                    await ctx.send(embed=prompt_effect())
                    etype = await self.bot.wait_for('message', check=check)
                    if not check_effect(etype.content.lower()) and etype.content.lower() != "done":
                        await ctx.send(embed=invalid_type(etype.content))
                        return
                    if etype.content.lower() != "done":
                        effects.append(etype.content.lower())
                    else:
                        effect = False
            await ctx.send(embed=prompt_afirm(item.content,variable.content,effects,description.content,name.content,link.content))
            afirm = await self.bot.wait_for('message', check=check)
            if afirm.content.lower() == "confirm":
                await ctx.send(embed=create_item(item.content,variable.content,effects,description.content,name.content,link.content))
            else:
                await ctx.send(embed=prompt_exit())
                
def setup(bot):
    bot.add_cog(Adventure(bot))

    


















def effect_types(operation,effect):
    ARMOR_EFFECTS = ["thorns"]
    WEAPON_EFFECTS = ["freezing", "bleeding", "healing"]
    SPELL_EFFECTS = ["poison"]
    
    VALID_EFFECTS = ARMOR_EFFECTS + WEAPON_EFFECTS + SPELL_EFFECTS
    
    if operation == "get":
        return VALID_EFFECTS
    elif operation == "check":
        if effect in VALID_EFFECTS:
            return True
        else:
            return False

    # effect_freezing() - Freezes the opponent
    # effect_thorns() - Enemy takes damage on attack
    # effect_bleeding() - Enemy takes damage each turn
    # effect_sharpness() - Increases your damage
    # effect_support() - Increases support damage
    # effect_healing() - Heals you x amount each turn
    # effect_heroic() - Heal allies x amount each turn
    # effect_rage() - Allows you to take 2 turns
    # effect_blinding() - Chance for enemy to miss
    # effect_weakness() - Lowers enemys attack damage
    #
    # 1 = The proc chance of the effect (decimal %)
    # 2 = The amount of that effect (intensity)
    # 3 = How many turns the effect lasts

##################################
########## Create Functions ##########
##################################
# Display functions save room in the main
# method by creating the embed content
# inside of a function. These can edited
# freely, as changing stuff wont usually
# affect the rest of the system.

def item_types(operation,item):
    
    # Here you can change / add new item types,
    # and the system will do the rest! Items can
    # be a part of one base class (health, armor,
    # damge) and the effect class (optional)
    #
    # HEALTH_CLASS = Adds health
    # ARMOR_CLASS = Negates % of damage
    # DAMAGE_CLASS = Does damage
    # SPELL_CLASS = Casts effect_type
    # EFFECT_CLASS = Applies effect
    
    HEALTH_CLASS = ["helmet", "armor", "ring"]
    ARMOR_CLASS = ["shield"]
    DAMAGE_CLASS = ["weapon"]
    SPELL_CLASS = ["spell"]
    EFFECT_CLASS = ["spell", "helmet", "armor", "ring", "weapon"]
    
    if operation == "check":
        if item.lower() in HEALTH_CLASS + ARMOR_CLASS + DAMAGE_CLASS + SPELL_CLASS:
            return True
        else:
            return False
    elif operation == "get":
        return HEALTH_CLASS + ARMOR_CLASS + DAMAGE_CLASS + SPELL_CLASS
    elif operation == "percentage":
        if item in ARMOR_CLASS:
            return True
        else:
            return False
    elif operation == "class":
        if item in HEALTH_CLASS:
            return "health"
        elif item in ARMOR_CLASS:
            return "armor"
        elif item in DAMAGE_CLASS:
            return "damage"
        else:
            return "spell"
    elif operation == "effect":
        if item in EFFECT_CLASS:
            return True
        else:
            return False

def create_item(a,b,c,d,e,h):
    g = item_types("class",a.lower())
    database="Axiiom/items.json"
    with open(database) as f:
        data = json.load(f)
    new_data = {
        "item_name": e.lower(),
        "item_type": a.lower(),
        "item_class": g,
        "item_variable": b,
        "item_description": d,
        "item_link": h,
        "item_effects": c
    }
    data.append(new_data)
    with open(database, "w") as f:
        json.dump(data, f, indent=4)
    return discord.Embed(title=f"Item Creator | Success!", description=f"The item has been saved in the database!",color=14957195)

def check_type(a):
    if item_types("check",a) is True:
        return True
    return False

def check_effect(a):
    if effect_types("check",a) is True:
        return True
    return False

def check_variable(a,b):
    if a < 1:
        return False
    elif item_types("percentage",b) is True:
        if a > 100:
            return False
    return True

def check_name(a):
    database="Axiiom/items.json"
    with open(database) as f:
        data = json.load(f)
    for scan in data:
        if scan["item_name"] == a:
            return False
    return True

def check_link(a):
    embed = discord.Embed(title="a", color=14957195)
    try:
        embed.set_image(url=a)
        return True
    except:
        return False

def prompt_variable(a):
    embed, effect, ctype = None, item_types("effect",a), item_types("class",a)
    if ctype == "health":
        embed = discord.Embed(title=f"Item Creator | New {a.capitalize()}", description=f"How much health should the {a} add?", color=14957195)
    elif ctype == "armor":
        embed = discord.Embed(title=f"Item Creator | New {a.capitalize()}", description=f"What % of damage should the {a} negate?", color=14957195)
    elif ctype == "damage":
        embed = discord.Embed(title=f"Item Creator | New {a.capitalize()}", description=f"How much damage should the {a} do?", color=14957195)
    return embed, effect

def prompt_item(a):
    display, items = "", item_types("get",None)
    for scan in items:
        display = display + f"\n- {scan.capitalize()}"
    return discord.Embed(title=f"Item Creator | New Item", description=f"What type of item is {a}?\n\n**Type one of the following...**{display}",color=14957195)

def prompt_effect():
    display, effects = "", effect_types("get",None)
    for scan in effects:
        display = display + f"\n- {scan.capitalize()}"
    return discord.Embed(title=f"Item Creator | Add Effect", description=f"Choose an effect to add! Type `done` when finished.\n\n**Type one of the following...**{display}",color=14957195)

def prompt_name():
    return discord.Embed(title=f"Item Creator | Name", description=f"Enter the name of the new item",color=14957195)

def prompt_description(a):
    return discord.Embed(title=f"Item Creator | Description", description=f"Enter the description of {a}",color=14957195)

def prompt_link(a):
    return discord.Embed(title=f"Item Creator | Image", description=f"Enter the image link for {a}\n\n**WARNING**\nEnsure the link is an image URL!",color=14957195)

def prompt_afirm(a,b,c,d,e,f):
    g = item_types("class",a.lower())
    embed = discord.Embed(title=f"Item Creator | Confirm Item", description=f"**Name:** {e}\n**Type:** {a.capitalize()}\n**Class:** {g.capitalize()}\n**Variable:** {b}\n**Effects:** {c}\n\n**Description**\n{d}\n\nType `confirm` to save the item!",color=14957195)
    embed.set_thumbnail(url=f)
    return embed

def prompt_exit(a):
    return discord.Embed(title="Item Creator | Cancelled Creation", description=f"Abonded item creation! The item was not saved.", color=discord.Color.red())

def invalid_type(a):
    return discord.Embed(title="Item Creator | Invalid Input", description=f"{a} is not a valid! Please double check the question.", color=discord.Color.red())

def invalid_name(a):
    return discord.Embed(title="Item Creator | Invalid Name", description=f"An item with the name {a} already exists!", color=discord.Color.red())





#################################
######### Display Functions ##########
#################################
# Display functions save room in the main
# method by creating the embed content
# inside of a function. These can edited
# freely, as changing stuff wont usually
# affect the rest of the system.
   
def display_stats(user):
    embed = discord.Embed(title=f"Stats | {user.name}", color=14957195)
    embed.add_field(name="Helmet", value="Nothing Equipped", inline=True)
    embed.add_field(name="Armor", value="Nothing Equipped", inline=True)
    embed.add_field(name="Ring", value="Nothing Equipped", inline=True)
    embed.add_field(name="Weapon", value="Nothing Equipped", inline=True)
    embed.add_field(name="Shield", value="Nothing Equipped", inline=True)
    embed.add_field(name="Spell", value="Nothing Equipped", inline=True)
    embed.add_field(name="\u200B", value="\u200B", inline=False)
    embed.add_field(name=f"Health ({get_hp(user.id)}/{get_max_hp(user.id)})", value=health_bar(user), inline=True)
    embed.add_field(name=f"Mana ({get_mana(user.id)}/{get_max_mana(user.id)})", value="<:Mana1:756218650679312406><:Mana2:756218650570260552><:Mana2:756218650570260552><:Mana2:756218650570260552><:Mana2:756218650570260552><:Mana2:756218650570260552><:Mana2:756218650570260552><:Mana2:756218650570260552><:Mana3:756218650704216114>", inline=True)
    embed.set_footer(text=f"0 items in inventory.")
    return embed

def health_bar(user):
    HP = (get_hp(user.id)/get_max_hp(user.id))*10
    H1 = "<:Full1:756001583032041603>"
    H2 = "<:Full2:756001583002550372>"
    H3 = "<:Full3:756001582801485856>"
    E1 = "<:Empty1:756001582667137186>"
    E2 = "<:Empty2:756001583036235897>"
    E3 = "<:Empty3:756001582595965089>"
    if HP <= 0:
        return E1+E2+E2+E2+E2+E2+E2+E2+E3
    elif HP <= 1:
        return H1+E2+E2+E2+E2+E2+E2+E2+E3
    elif HP <= 2:
        return H1+H2+E2+E2+E2+E2+E2+E2+E3
    elif HP <= 3:
        return H1+H2+H2+E2+E2+E2+E2+E2+E3
    elif HP <= 4:
        return H1+H2+H2+H2+E2+E2+E2+E2+E3
    elif HP <= 5:
        return H1+H2+H2+H2+H2+E2+E2+E2+E3
    elif HP <= 6:
        return H1+H2+H2+H2+H2+H2+E2+E2+E3
    elif HP <= 7:
        return H1+H2+H2+H2+H2+H2+H2+E2+E3
    elif HP <= 8:
        return H1+H2+H2+H2+H2+H2+H2+H2+E3
    else:
        return H1+H2+H2+H2+H2+H2+H2+H2+H3

   
#################################
########## Event Functions ##########
#################################
# Event functions deal with specific things
# that may occur in a battle. These could
# range from a player dying, all the way
# to a player freezing an enemy.
   
def on_death(uuid):
    maxhp = get_max_hp(uuid)
    response = set_hp(uuid, maxhp)
    if response == 0:
        return False
    elif response == 1:
        return True
    else:
        #set_death(uuid)
        return True

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
        response = set_hp(uuid, 0)
        return False

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
                elif b < scan["current_mana"]:
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







    # Here you can change / add new effect types,
    # and the system will do the rest! Adding a new
    # effect will automaticaly make it eligible to be
    # applied, but you must tell the program what
    # to do with it. To do this, add an if-statement
    # under the "apply" section telling the program
    # to look for the effect type, then type in any
    # of the following effect events in it...
    #