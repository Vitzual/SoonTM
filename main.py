# import all needed imports
import discord
from discord.ext import commands
from discord.utils import get
import random
import math
import traceback
import sys
import json
import datetime

TOKEN = "TOKEN HERE"  # Bot token -- used to push code to bot
bot = commands.Bot(command_prefix="!", description="Syntax: <needed> [optional] [option1|option2]\nMade by Vitzual")
startup_extensions = ["Cog.admin", "Cog.reload", "Cog.games", "Cog.economy", "Cog.experience", "Cog.adventure"] # Load commands via COG

@bot.event 
async def on_ready():
    print(f"Connected {bot.user}")  # Send message on connection

@bot.event
async def on_message(message):
    if message.author.id == 716704555890507887:
        return
    elif message.channel.id != 749434411648417854:
        print(f"({message.author} in {message.channel.name}) : {message.content}")
        return
    elif message.content.startswith('!'):
        await bot.process_commands(message)
        return
    else:
        db,index,bypass = "Axiiom/user_ranks.json",0,False
        with open(db) as f:
            xpdb = json.load(f)
        for scan in xpdb:
            if scan["user_id"] == message.author.id:
                new_data = {
                  "user_id": scan["user_id"],
                  "xp": int(scan["xp"]+random.randint(5, 10)),
                  "rank": scan["rank"]
                }
                xpdb.append(new_data)
                del xpdb[index]
                with open(db, "w") as f:
                    json.dump(xpdb, f, indent=4)
                operation = check_rankup(message.author.id, scan["xp"], new_data["xp"])
                if operation == 1:
                    embed = discord.Embed(title=f"{message.author.name} | Level Up!", description=f"You have leveled up to level {check_level(message.author.id)}!", color=14957195)
                    await message.channel.send(embed=embed)
                elif operation == 2:
                    rank = bot.get_role({check_rank(message.author.id)})
                    await message.author.add_roles(rank)
                    embed = discord.Embed(title=f"{message.author.name} | Rank Up!", description=f"Congratulations! You ranked up to {rank.mention}!", color=14957195)
                    await message.channel.send(embed=embed)
                bypass = True
            index+=1
        if not bypass:
            new_data = {
              "user_id": message.author.id,
              "xp": random.randint(5, 10),
              "rank": 568614562526396427
            }
            xpdb.append(new_data)
            with open(db, "w") as f:
                json.dump(xpdb, f, indent=4)
        blacklist, mod = "Axiiom/blacklist.json", True
        with open(blacklist) as f:
            data = json.load(f)
        for look in message.author.roles:
            if look.name == "Moderator":
                mod = True
        if mod:
            return
        for scan in data[0]["words"]:
            if scan.lower() in message.content.lower() and message.channel.id in data[0]["channels"]:
                database = "Axiiom/user_records.json"
                with open(database) as f:
                    records = json.load(f)
                index = 0
                bypass = False
                for look in records:
                    if look["user_id"] == message.author.id:
                        look["warns"].append("We do not tolerate vulgar language on the server.")
                        new_data = {
                            "user_id": look["user_id"],
                            "warns": look["warns"]
                        }
                        records.append(new_data)
                        with open(database, "w") as f:
                            json.dump(records, f, indent=4)
                        del records[index]
                        with open(database, "w") as f:
                            json.dump(records, f, indent=4)
                        bypass = True
                        index+=1
                if not bypass:
                    new_data = {
                        "user_id": message.author.id,
                        "warns": ["We do not tolerate vulgar language on the server."]
                    }
                    records.append(new_data)
                    with open(database, "w") as f:
                        json.dump(records, f, indent=4)
                await message.delete()
                embed = discord.Embed(title=f"Warning | Blacklisted Word", description=f"Your message has been removed {message.author.mention}\n\n**Auto warned**\nWe do not tolerate vulgar language on the server.", color=discord.Color.red())
                await message.channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    # If command has local error handler, return
    if hasattr(ctx.command, 'on_error'):
        return

    # Get the original exception
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=f"Argument error", description=f"You forgot to all the variables! Check what you need with {bot.command_prefix}help {ctx.command}`", color=discord.Color.red())
        embed.set_footer(text=f"{error}")
        await ctx.send(embed=embed)

    if isinstance(error, commands.BotMissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
        embed = discord.Embed(title=f"Permission error", description='I need the **{}** permission(s) to run this command.'.format(fmt), color=discord.Color.red())
        embed.set_footer(text=f"{error}")
        await ctx.send(embed=embed)
        return

    if isinstance(error, commands.DisabledCommand):
        embed = discord.Embed(title=f"Disabled error", description="This command has been disabled", color=discord.Color.red())
        embed.set_footer(text=f"{error}")
        await ctx.send(embed=embed)
        return

    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title=f"Woah there cowboy!", description=f"That command has a cooldown!", color=discord.Color.red())
        embed.set_footer(text=f"Please try again in {format(math.ceil(error.retry_after))}s")
        await ctx.send(embed=embed)
        return

    if isinstance(error, commands.MissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
        embed = discord.Embed(title=f"Permission error",
                              description=f"{_message}",
                              color=discord.Color.red())
        embed.set_footer(text=f"{error}")
        await ctx.send(embed=embed)
        return

    if isinstance(error, commands.NoPrivateMessage):
        try:
            embed = discord.Embed(title=f"DM error",
                                  description="This command cannot be sued in direct messages",
                                  color=discord.Color.red())
            embed.set_footer(text=f"{error}")
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            pass
        return

    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=f"Permission error",
                              description=f"You do not have permission to use this command",
                              color=discord.Color.red())
        embed.set_footer(text=f"{error}")
        await ctx.send(embed=embed)
        return

    # ignore all other exception types, but print them to stderr
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)

    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

if __name__ == "__main__":  # When script is loaded, this will run
  bot.remove_command("help")
  for extension in startup_extensions:
    try:
      bot.load_extension(extension)  # Loads cogs successfully
    except Exception as e:
      exc = '{}: {}'.format(type(e).__name__, e)
      print('Failed to load extension {}\n{}'.format(extension, exc))  # Failed to load cog, with error

def load(db, uid):
  try:
    with open(db) as f:
      data = json.load(f)
  except Exception as ex:
    print(ex)
  else:
    index = 0
    for scan in data:
      if scan["user_id"] == uid:
        return data, scan, index 
      index+=1
  return data, False, False

def check_rankup(a, b, c):
    if int(0.16 * math.sqrt(b)) < int(0.16 * math.sqrt(c)):
        database = "Axiiom/xp_ranks.json"
        with open(database) as f:
            data = json.load(f)
        index, holder = 0, 0
        for scan in data:
            if scan["requirement"] > largest:
                largest, holder = scan["requirement"], index
            index+=1
        database,index = "Axiiom/user_ranks.json",0
        with open(database) as f:
            ranks = json.load(f)
        for scan in ranks:
            if scan["user_id"] == a:
                if data[holder]["rank"] != scan["rank"]:
                    new_data = {
                      "user_id": scan["user_id"],
                      "xp": scan["xp"],
                      "rank": data[holder]["rank"]
                    }
                    ranks.append(new_data)
                    del ranks[index]
                    with open(database, "w") as f:
                        json.dump(ranks, f, indent=4)
                    return 2
                else:
                    return 1
            index+=1
    return 0
    
def check_level(a):
    return int(0.16 * math.sqrt(a))

def check_rank(a):
    database = "Axiiom/user_ranks.json",0
    with open(database) as f:
        ranks = json.load(f)
    for scan in ranks:
        if scan["user_id"] == a:
            return scan["rank"]
    return 568614562526396427












bot.run(TOKEN)
