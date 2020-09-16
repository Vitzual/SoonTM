import discord
import json
import random
import asyncio
import datetime
from discord.ext import commands, tasks
from discord.utils import get

class Games(commands.Cog, name="Games"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ["games"])
    async def minigames(self, ctx, operation = "", amount:int = 0):
        # User check (for when prompted to input something)
        # Without it, anyone could respond to a prompt
        def check(m):
            return m.author == ctx.author
        # Main panel
        if operation == "":
            embed = discord.Embed(title=f"Minigames | Command List", description="Play minigames and earn guags!\n\n**Dice roll:** `!minigames roll [amount]`\nRoll two dice and if they match, you win!\n\n**Coin flip:** `!minigames flip [amount]`\nBet guags and flip a coin to double or nothing!\n\n**Memory match:** `!minigames memory [amount]`\nBet guags and put your memory to the test!\n\n**High low:** `!minigames highlow [amount]`\nBet guags on if the next card is high or low!\n\n**Reaction time:** `!minigames time [amount]`\nReact to a message in under 0.5 seconds to win!\n:warning: **Not recommended if you have high ping!**", color=14957195)
            embed.set_thumbnail(url="https://i.ibb.co/rFMdyLL/Untitled-2.png")
            await ctx.channel.send(embed=embed)
            return
        # Enables the status switch if it's disabled
        elif operation == "enable":
            for scan in ctx.author.roles:
                if scan.name == "Moderator":
                    if isActive():
                        embed = discord.Embed(title="Minigames | Status Switch", description="Minigames already enabled via status.", color=14957195)
                    else:
                        embed = discord.Embed(title="Minigames | Status Switch", description="Enabled minigames via status switch.", color=14957195)
                        activate() # The activate() and deactivate() methods call the database and change the active index to the new status 
                    await ctx.channel.send(embed=embed)
            return
        # Disables the status switch if it's enabled
        elif operation == "disable":
            for scan in ctx.author.roles:
                if scan.name == "Moderator":
                    if isActive():
                        embed = discord.Embed(title="Minigames | Status Switch", description="Disabled minigames via status switch.", color=14957195)
                        deactivate()
                    else:
                        embed = discord.Embed(title="Minigames | Status Switch", description="Minigames already disabled via status.", color=14957195)
                    await ctx.channel.send(embed=embed)
            return
        # Displays what the switch status is currently set to
        elif operation == "status":
            for scan in ctx.author.roles:
                if scan.name == "Moderator":
                    if isActive():
                        embed = discord.Embed(title="Minigames | Status Switch", description="Minigames are currently enabled.", color=14957195)
                    else:
                        embed = discord.Embed(title="Minigames | Status Switch", description="Minigames are currently disabled.", color=14957195)
                    await ctx.channel.send(embed=embed)
            return
        # Checks to see if status switch is active. If so returns
        if isActive():
            embed = discord.Embed(title="Minigames | Active Game", description="Please wait for the current game to end", color=discord.Color.red())
            await ctx.channel.send(embed=embed)
            return
        # Memory game
        if operation == "memory":
            if amount <= 9 or amount >= 51:
                embed = discord.Embed(title="Minigames | Memory Match", description="Please enter between 10-50 guags!", color=14957195)
                await ctx.channel.send(embed=embed)
                return
            elif validbal(ctx.author.id, amount) is False:
                embed = discord.Embed(title="Minigames | Memory Match", description="You don't have enough guags to bet that!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            # Setup area, don't mess with this (and yes I could've tidied this up even mnore but guess what I didn't, big shocker I know)
            activate()
            core = getcore()
            hidden = getlist() + getlist()
            random.shuffle(hidden)
            disp = "**Welcome to memory match!**"
            turns = 10
            pairs = 6
            game = True
            board = await ctx.channel.send(display(core))
            embed = discord.Embed(title="Minigames | Memory Match", description=f"{disp}\nPick two different emojis to flip.\n**Ex:** `1 3`, `3 2`, `5 6`, etc\n\n**Pairs:** {pairs} left\n**Lives:** {turns} left", color=14957195)
            message = await ctx.channel.send(embed=embed)
            # Endless itteration loops are bad practice. Don't do it kids. 
            while game:
                if disp != "**Welcome to memory match!**":
                    embed = discord.Embed(title="Minigames | Memory Match", description=f"{disp}\nPick two different emojis to flip.\n**Ex:** `1 3`, `3 2`, `5 6`, etc\n\n**Pairs:** {pairs} left\n**Lives:** {turns} left", color=14957195)
                    await message.edit(embed=embed)
                    await guess.delete()
                    if pairs == 0:
                        embed = discord.Embed(title="Minigames | Memory Match", description=f"**Game over!** You matched all the pairs!\nYou earned {amount} guags.", color=14957195)
                        await board.edit(content=display(hidden))
                        await ctx.send(embed=embed)
                        payout(ctx.author.id, amount)
                        deactivate()
                        return
                    elif turns == 0:
                        embed = discord.Embed(title="Minigames | Memory Match", description=f"**Game over!** You ran out of turns!\nYou lost {amount} guags.", color=discord.Color.red())
                        await board.edit(content=display(hidden))
                        await ctx.send(embed=embed)
                        payout(ctx.author.id, -amount)
                        deactivate()
                        return
                    else:
                        await board.edit(content=display(core))
                try:
                    guess = await self.bot.wait_for('message', timeout=30.0, check=check)
                    num1, num2 = parse(guess.content)
                except Exception as e:
                    embed = discord.Embed(title="Minigames | Memory Match", description=f"**Game over!** You took too long to reply!\nYou lost {amount} guags.", color=discord.Color.red())                        
                    await ctx.channel.send(embed=embed)
                    deactivate()
                    return
                valid,disp = isValid(num1,num2,core,hidden)
                if valid:
                    if disp == "matching":
                        disp = ":tada: **Correct! You matched two pairs!**"
                        core[num1] = hidden[num1]
                        core[num2] = hidden[num2]
                        pairs-=1
                    else:
                        embed = discord.Embed(title="Minigames | Memory Match", description=f":x: **Incorrect! Memorize these emojis.**\n**Warning:** This will disappear in 5 seconds!", color=14957195)
                        hold = [core[num1], core[num2]]
                        core[num1] = hidden[num1]
                        core[num2] = hidden[num2]
                        await board.edit(content=display(core))
                        await message.edit(embed=embed)
                        await asyncio.sleep(5)
                        core[num1] = hold[0]
                        core[num2] = hold[1]
                        disp = ":x: **Incorrect! Now try again.**"
                        turns-=1
        # High low game
        elif operation == "highlow":
            if amount < 10 or amount > 50:
                embed = discord.Embed(title="Minigames | Dice Roll", description="Please enter between 10-50 guags!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            elif validbal(ctx.author.id, amount) is False:
                embed = discord.Embed(title="Minigames | Dice Roll", description="You don't have enough guags to bet that!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            # Setup variables for game again. Don't @ me for not using getters and setters.
            activate()
            gameover = False
            reward = 0
            turns = 1
            guess = "first"
            card = 1 # Initiation
            while not gameover:
                previous = card
                card = random.randint(2,14)
                suit = random.randint(1,4)
                # Realizing now I could've turned this into a method but guess what I didn't so... 
                if card == 11:
                    extension = "Jack"
                elif card == 12:
                    extension = "Queen"
                elif card == 13:
                    extension = "King"
                elif card == 14:
                    extension = "Ace"
                else:
                    extension = f"{card}"
                if suit == 1:
                    extension = extension + " of Spades"
                elif suit == 2:
                    extension = extension + " of Hearts"
                elif suit == 3:
                    extension = extension + " of Clubs"
                else:
                    extension = extension + " of Diamonds"
                if guess == "higher":
                    if card >= previous:
                        reward+=int(amount*0.25)
                        stats = f"\n:tada: You drew a **{extension}** (+{int(amount*0.25)} guags)"
                    else:
                        reward-=int(amount*0.5)
                        stats = f"\n:x: You drew a **{extension}** (-{int(amount*0.5)} guags)"
                elif guess == "lower":
                    if card >= previous:
                        reward-=int(amount*0.5)
                        stats = f"\n:x: You drew a **{extension}** (-{int(amount*0.5)} guags)"
                    else:
                        reward+=int(amount*0.25)
                        stats = f"\n:tada: You drew a **{extension}** (+{int(amount*0.25)} guags)"
                else:
                    stats = f"You drew a **{extension}**!"
                    embed = discord.Embed(title="Minigames | High Low", description=f"{stats}\n*Will the next draw be `higher` or `lower`?*\n\n**Earnings:** {reward} guags\n**Turns:** {11-turns} left", color=14957195)
                    message = await ctx.channel.send(embed=embed)
                if guess != "first":
                    embed = discord.Embed(title="Minigames | High Low", description=f"{stats}\n*Will the next draw be `higher` or `lower`?*\n\n**Earnings:** {reward} guags\n**Turns:** {11-turns} left", color=14957195)
                    await message.edit(embed=embed)
                    await a.delete()
                if turns == 11:
                    embed = discord.Embed(title="Minigames | High Low", description=f"**Game over!** You ran out of turns!\nYou ended up with {reward} guags.", color=14957195)
                    await ctx.channel.send(embed=embed)
                    payout(ctx.author.id, reward)
                    deactivate()
                    return
                elif reward <= -amount:
                    embed = discord.Embed(title="Minigames | High Low", description=f"**Game over!** You hit your bet amount!\nYou ended up with -{amount} guags.", color=14957195)
                    await ctx.channel.send(embed=embed)
                    payout(ctx.author.id, -amount)
                    deactivate()
                    return
                elif reward >= amount:
                    embed = discord.Embed(title="Minigames | High Low", description=f"**Game over!** You hit your bet amount!\nYou ended up with {amount} guags.", color=14957195)
                    await ctx.channel.send(embed=embed)
                    payout(ctx.author.id, amount)
                    deactivate()
                    return
                else:
                    turns+=1
                try:
                    a = await self.bot.wait_for('message', timeout=20.0, check=check)
                    guess = a.content.lower()
                except:
                    embed = discord.Embed(title="Minigames | High Low", description=f"**Game over!** You took too long to reply!\nYou ended up with {reward} guags!", color=discord.Color.red())
                    await ctx.channel.send(embed=embed)
                    payout(ctx.author.id, reward)
                    deactivate()
                    return
                if guess != "higher" and guess != "lower":
                    embed = discord.Embed(title="Minigames | High Low", description=f"You responded with an invalid choice!\n**Game over!** You ended up with {reward} guags.", color=discord.Color.red())
                    await ctx.channel.send(embed=embed)
                    payout(ctx.author.id, reward)
                    deactivate()
                    return
        elif operation == "roll":
            if amount <= 0 or amount >= 11:
                embed = discord.Embed(title="Minigames | Dice Roll", description="Please enter between 1-10 guags!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            elif validbal(ctx.author.id, amount) is False:
                embed = discord.Embed(title="Minigames | Dice Roll", description="You don't have enough guags to bet that!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            activate()
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            if dice1 == dice2:
                embed = discord.Embed(title="Minigames | Dice Roll", description=f"You rolled two **{dice1}**'s and won {amount} guags, nice!", color=14957195)
                await ctx.channel.send(embed=embed)
                payout(ctx.author.id, amount)
                deactivate()
                return
            else:
                embed = discord.Embed(title="Minigames | Dice Roll", description=f"Uh oh! You rolled a **{dice1}** and a **{dice2}**.", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                payout(ctx.author.id, -amount)
                deactivate()
                return
        elif operation == "flip":
            if amount <= 0 or amount >= 6:
                embed = discord.Embed(title="Minigames | Coin Flip", description="Please enter between 1-5 guags!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            elif validbal(ctx.author.id, amount) is False:
                embed = discord.Embed(title="Minigames | Coin Flip", description="You don't have enough guags to bet that!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            activate()
            embed = discord.Embed(title="Minigames | Coin Flip", description=f"Pick a side, heads or tails!", color=14957195)
            message = await ctx.channel.send(embed=embed)
            try:
                side = await self.bot.wait_for('message', timeout=10.0, check=check)
            except:
                embed = discord.Embed(title="Minigames | Coin Flip", description="You took too long to reply!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                deactivate()
                return
            if side.content.lower() != "heads" and side.content.lower() != "tails":
                embed = discord.Embed(title="Minigames | Coin Flip", description="Invalid side! Valid sides are `heads` or `tails`", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                deactivate()
                return
            fliparoo = random.randint(1, 2)
            if fliparoo == 1:
                face = "heads"
            else:
                face = "tails"
            if (fliparoo == 1 and side.content.lower() == "heads") or (fliparoo == 2 and side.content.lower() == "tails"):
                embed = discord.Embed(title="Minigames | Coin Flip", description=f"It was {face}! You won {amount} guags!", color=14957195)
                message = await ctx.channel.send(embed=embed)
                payout(ctx.author.id, amount)
            else:
                embed = discord.Embed(title="Minigames | Coin Flip", description=f"It was {face}! You lost {amount} guags!", color=discord.Color.red())
                message = await ctx.channel.send(embed=embed)
                payout(ctx.author.id, -amount)
        elif operation == "time":
            if amount < 1 or amount > 11:
                embed = discord.Embed(title="Minigames | Reaction Time", description="Please enter between 1-10 guags!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            elif validbal(ctx.author.id, amount) is False:
                embed = discord.Embed(title="Minigames | Reaction Time", description="You don't have enough guags to bet that!", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                return
            activate()
            embed = discord.Embed(title="Minigames | Reaction Time", description=f"When I say shoot, respond with anything.\n**Message will be sent in next 15 seconds...**", color=14957195)
            message = await ctx.channel.send(embed=embed)
            await asyncio.sleep(random.randint(5, 15))
            mgs = []
            async for x in ctx.channel.history(limit=100):
                if x.id == message.id:
                    break
                else:
                    if x.author == ctx.author:
                        embed = discord.Embed(title="Minigames | Reaction Time", description=f"You sent a message before the shot!\n**You lost {amount} guag(s).**", color=discord.Color.red())
                        await ctx.channel.send(embed=embed)
                        payout(ctx.author.id, -amount)
                        deactivate()
                        return
            embed = discord.Embed(title="Shoot!", color=14957195)
            await ctx.channel.send(embed=embed)
            start = datetime.datetime.now()
            try:
                check = await self.bot.wait_for('message', timeout=10.0, check=check)
            except:
                embed = discord.Embed(title="Minigames | Reaction Time", description=f"You took too long to reply!\n**You lost {amount} guag(s).**", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                payout(ctx.author.id, -amount)
                deactivate()
                return
            end = datetime.datetime.now()
            time = round((end - start).total_seconds(), 3)
            if time <= 0.5:
                embed = discord.Embed(title="Minigames | Reaction Time", description=f"You reacted in {time}s!\n**You won {amount} guag(s).**", color=14957195)
                await ctx.channel.send(embed=embed)
                payout(ctx.author.id, amount)
            else:
                embed = discord.Embed(title="Minigames | Reaction Time", description=f"You reacted in {time}s!\n**You lost {amount} guag(s).**", color=discord.Color.red())
                await ctx.channel.send(embed=embed)
                payout(ctx.author.id, -amount)
        else:
            embed = discord.Embed(title="Minigames | Invalid Selection", description="Get a list of valid games using `!minigames`", color=discord.Color.red())
            await ctx.channel.send(embed=embed)
        deactivate()

def isActive():
    database="Axiiom/game_switch.json"
    with open(database) as f:
        data = json.load(f)
    if data[0]["active"] == 1:
        return True
    else:
        return False

def activate():
    database="Axiiom/game_switch.json"
    with open(database) as f:
        data = json.load(f)
    new_data = {
        "active": 1
    }
    del data[0]
    data.append(new_data)
    with open(database, "w") as f:
        json.dump(data, f, indent=4)
    return

def deactivate():
    database="Axiiom/game_switch.json"
    with open(database) as f:
        data = json.load(f)
    new_data = {
        "active": 0
    }
    del data[0]
    data.append(new_data)
    with open(database, "w") as f:
        json.dump(data, f, indent=4)
    return

def isValid(a,b,c,d):
    if a == b:
        return False, ":x: **You must choose two different numbers!**"
    elif c[a] == d[a] or c[b] == d[b]:
        return False, ":x: **You cannot choose a flipped emoji!**"
    elif a > 11 or a < 0 or b > 11 or b < 0:
        return False, f":x: **You must choose between 1-12!** ({a} {b})"
    elif d[a] == d[b]: 
        return True, "matching"
    else:
        return True, "unmatching"

def getcore(a,b):
    c = []
    d = 0
    while d != 4:
        c.append(b[a+d])
        d+=1
    return c

def parse(a):
    b = a.split()
    numA = int(b[0]) - 1
    numB = int(b[1]) - 1
    return numA, numB

def display(a):
    disp = ""
    index=0
    for scan in a:
        disp = disp + scan + " "
        if index == 3 or index == 7 or index ==11:
            disp = disp + "\n"
        index+=1
    return disp

def getcore():
    # This is the board faces. You can change these to any valid emoji
    return ["<:1:753631039699550238>", "<:2:753631059236880385>", "<:3:753631075346939965>", "<:4:753631091641810998>", "<:5:753631103239192718>", "<:6:753631116484804690>", "<:7:753631130330333205>", "<:8:753631140635607084>", "<:9:753631154409570496>", "<:10:753631166942412840>", "<:11:753631179160420471>", "<:12:753631189708832790>"]

def getlist():
    # This is the board pieces. You can change these to any valid emoji
    return ["<:CardWump:753634310161956915>", "<:CardPachi:753638273678835842>", "<:CardMel:753634371810099230>", "<:CardGuag:753634236409577573>", "<:CardFriendly:753638221077807136>", "<:CardAxiiom:753638179508060162>"]

def validbal(uuid,a):
    database="Axiiom/user_economy.json"
    with open(database) as f:
        data = json.load(f)
    index = 0
    for scan in data:
        if scan["user_id"] == uuid:
            if scan["balance"] >= a:
                return True
            else:
                return False
    return False
    
def payout(uuid,a):
    database="Axiiom/user_economy.json"
    with open(database) as f:
        data = json.load(f)
    index = 0
    for scan in data:
        if scan["user_id"] == uuid:
            new_data = {
            "user_id": uuid,
            "balance": int(scan["balance"]+a)
            }
            del data[index]
            data.append(new_data)
            with open(database, "w") as f:
                json.dump(data, f, indent=4)
        index+=1

def setup(bot):
    bot.add_cog(Games(bot))