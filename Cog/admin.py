import discord
import random
import json
import asyncio
from discord.ext import commands, tasks
from discord.utils import get
from collections.abc import Sequence

# 14957195

class Admin(commands.Cog, name="Admin"):
    """Admin commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("Moderator")
    @commands.command()
    async def warn(self, ctx, operation:str = "", user: discord.Member = None, *, reason: str = ""):
      if operation == "" and user is None and reason == "":
        embed = discord.Embed(title=f"Warn | Command List", description="Track and modify a users warns record.\n\n**Add warning:** `!warn add [user] [reason]`\nAdds a warning to a users record\n\n**Remove warning:** `!warn remove [user] [number]`\nRemoves warning from a users record\n\n**View record:** `!warn record [user]`\nDisplays a users warns record", color=14957195)
        embed.set_thumbnail(url="https://i.ibb.co/rFMdyLL/Untitled-2.png")
        await ctx.send(embed=embed)
        return
      operation = operation.lower()
      if operation != "add" and operation != "remove" and operation != "record":
        embed = discord.Embed(title=f"Warn | Invalid Operation", description=f"Valid operations are `add`, `remove`, and `record`!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
      if user is None:
        if operation == "record":
            user = ctx.author
        else:
          embed = discord.Embed(title=f"Warn | Invalid User", description=f"Please specify a valid user.", color=discord.Color.red())
          await ctx.send(embed=embed)
          return
      if operation == "add":
        if reason == "":
          embed = discord.Embed(title=f"Warn | Reason Unspecified", description=f"Please specify a valid reason.", color=discord.Color.red())
          await ctx.send(embed=embed)
          return
        for scan in user.roles:
          if scan.name == "Administrator":
            embed = discord.Embed(title=f"Warn Vetoed", description=f"{user.name} is immune to warns!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        database = "Axiiom/user_records.json"
        with open(database) as f:
          data = json.load(f)
        index = 0
        for scan in data:
          if scan["user_id"] == user.id:
            scan["warns"].append(reason)
            new_data = {
              "user_id": scan["user_id"],
              "warns": scan["warns"]
            }
            data.append(new_data)
            with open(database, "w") as f:
              json.dump(data, f, indent=4)
            del data[index]
            with open(database, "w") as f:
              json.dump(data, f, indent=4)
            embed = discord.Embed(title=f"Warned {user.name}", description=f"{user.name} was warned by {ctx.author.name}\n\n**Reason:** {reason}", color=14957195)
            await ctx.send(embed=embed)
            return
          index+=1
        new_data = {
          "user_id": user.id,
          "warns": [reason]
        }
        data.append(new_data)
        with open(database, "w") as f:
          json.dump(data, f, indent=4)
        embed = discord.Embed(title=f"Warned {user.name}", description=f"{user.name} was warned by {ctx.author.name}\n\n**Reason:** {reason}", color=14957195)
        await ctx.send(embed=embed)
      elif operation == "remove":
        try:
          number = int(reason)
          number-=1
        except Exception:
          embed = discord.Embed(title=f"Warn | Invalid Number", description=f"Select a valid warn to remove!", color=discord.Color.red())
          await ctx.send(embed=embed)
          return
        database = "Axiiom/user_records.json"
        with open(database) as f:
          data = json.load(f)
        index = 0
        for scan in data:
          if scan["user_id"] == user.id:
            try:
              warning = scan["warns"].pop(number)
            except:
              embed = discord.Embed(title=f"Warn | Invalid Number", description=f"Select a valid warn to remove!", color=discord.Color.red())
              await ctx.send(embed=embed)
              return
            if len(scan["warns"]) != 0:
              new_data = {
                "user_id": scan["user_id"],
                "warns": scan["warns"]
              }
              data.append(new_data)
              with open(database, "w") as f:
                json.dump(data, f, indent=4)
            del data[index]
            with open(database, "w") as f:
              json.dump(data, f, indent=4)
            embed = discord.Embed(title=f"Warn | Pardoned {user.name}", description=f"{user.name} was pardoned by {ctx.author.name}\n\n**Removed warning:** {warning}", color=14957195)
            await ctx.send(embed=embed)
            return
          index+=1
        embed = discord.Embed(title=f"Warn | Pardon User", description="This use has no warns on record", color=14957195)
        await ctx.send(embed=embed)
      elif operation == "record":
        database = "Axiiom/user_records.json"
        mod = True
        if user != ctx.author:
            mod = False
            for scan in ctx.author.roles:
                if scan.name == "Moderator":
                    mod = True
        if not mod:
            embed = discord.Embed(title=f"Warn | No Permission", description="You cannot view other peoples records!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        with open(database) as f:
          data = json.load(f)
        for scan in data:
          if scan["user_id"] == user.id:
            total = len(scan["warns"])
            if total == 1:
              description = f"{user.name} has 1 warn on record!\n\n"
            else:
              description = f"{user.name} has {total} warns on record!\n\n"
            index = 1
            for warn in scan["warns"]:
              description = description + f"**{index})** {warn}\n"
              index+=1
            embed = discord.Embed(title=f"Warn | {user.name}'s Record", description=description, color=14957195)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=f"Warn | {user.name}'s Record", description="This user has no warns on record", color=14957195)
        await ctx.send(embed=embed)
      else:
        embed = discord.Embed(title=f"Warn | Invalid Operation", description=f"Valid operations are `add`, `remove`, and `record`!", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.has_role("Moderator")
    @commands.command()
    async def clear(self, ctx, amount:int = -1, user:discord.Member = None):
      if amount == -1 and user == None:
        embed = discord.Embed(title="Clear Messages | Commands List", description="Clear multiple messages at once.\n\n**Clear Channel:** `!clear [amount]`\nDeletes x amount of messages in channel\n\n**Clear User:** `!clear [amount] [user]`\nDeletes x amount of messages from user\n\n**--------------- IMPORTANT ---------------**\nAmount refers to how many messages to\ncheck, not how many to delete. Because\nof this, numbers may vary when used in\nnew channels or on users.", color=14957195)
        embed.set_thumbnail(url="https://i.ibb.co/rFMdyLL/Untitled-2.png")
        await ctx.send(embed=embed)
      elif user == None:
        total = await ctx.channel.purge(limit=amount+1)
        embed = discord.Embed(title="Clear Messages | Channel Wipe", description=f"Successfully cleared {len(total)} messages!", color=14957195)
        temp = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await temp.delete()
      else:
        def check(message):
          return message.author == user
        total = await ctx.channel.purge(limit=amount+1,check=check)
        embed = discord.Embed(title="Clear Messages | User Wipe", description=f"Successfully cleared {len(total)} messages from {user.mention}!", color=14957195)
        temp = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await temp.delete()
        
    @commands.has_role("Moderator")
    @commands.command()
    async def blacklist(self, ctx, operation: str = "", word: str = ""):
      if operation == "":
        embed = discord.Embed(title="Blacklist | Commands List", description="Blacklisted words get removed in chat.\n\n**View list:** `!blacklist list`\nView all blacklisted words\n\n**Add a word:** `!blacklist add`\nAdd a word to the blacklist\n\n**Remove a word:** `!blacklist remove`\nRemove a word from the blacklist\n\n**Enable a channel:** `!blacklist enable`\nEnable blacklist filtering on a channel\n\n**Disable a channel:** `!blacklist disable`\nDisable blacklist filtering on a channel", color=14957195)
        embed.set_thumbnail(url="https://i.ibb.co/rFMdyLL/Untitled-2.png")
        await ctx.send(embed=embed)
        return
      database = "Axiiom/blacklist.json"
      with open(database) as f:
        data = json.load(f)
      if operation.lower() == "list":
        description = "Overview of all words and channels.\n\n**Blacklist Words:**\n"
        scanned = False
        for scan in data[0]["words"]:
          description = description + "- " + scan.capitalize() + "\n"
          scanned = True
        if not scanned:
          description = description + "Nothing to display here\n"
        scanned = False
        description = description + "\n**Enabled Channels:**\n"
        for scan in data[0]["channels"]:
          channel = self.bot.get_channel(scan)
          if channel is not None:
            description = description + f"- <#{scan}>\n"
            scanned = True        
        if not scanned:
          description = description + "Nothing to display here\n"
        if description == "":
          embed = discord.Embed(title="Blacklist | List Overview", description="Nothing to display", color=14957195)
        else:
          embed = discord.Embed(title="Blacklist | List Overview", description=description, color=14957195)
        await ctx.send(embed=embed)
        return
      if operation.lower() == "add":
        if word == "":
          embed = discord.Embed(title="Blacklist | Add Word", description="Type `!blacklist add [word]` to add a word.", color=14957195)
          await ctx.send(embed=embed)
          return
        else:
          wordset = data[0]["words"]
          if word.lower() in wordset:
            embed = discord.Embed(title="Blacklist | Add Word", description="That word has already been added!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
          wordset.append(word.lower())
          new_data = {
            "words": wordset,
            "channels": data[0]["channels"]
          }
          data.append(new_data)
          with open(database, "w") as f:
            json.dump(data, f, indent=4)
          del data[0]
          with open(database, "w") as f:
            json.dump(data, f, indent=4)
          embed = discord.Embed(title="Blacklist | Add Word", description=f"Added `{word}` to blacklist!", color=14957195)
          await ctx.send(embed=embed)
        return
      if operation.lower() == "remove":
        if word == "":
          embed = discord.Embed(title="Blacklist | Remove Word", description="Type `!blacklist remove [word]` to remove a word.", color=14957195)
          await ctx.send(embed=embed)
          return
        else:
          wordset = data[0]["words"]
          if word.lower() not in wordset:
            embed = discord.Embed(title="Blacklist | Remove Word", description="That word isn't in the blacklist!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
          else:
            wordset.remove(word.lower())
            new_data = {
              "words": wordset,
              "channels": data[0]["channels"]
            }
            data.append(new_data)
            with open(database, "w") as f:
              json.dump(data, f, indent=4)
            del data[0]
            with open(database, "w") as f:
              json.dump(data, f, indent=4)
            embed = discord.Embed(title="Blacklist | Remove Word", description=f"Removed `{word}` from blacklist!", color=14957195)
            await ctx.send(embed=embed)
        return
      if operation.lower() == "enable":
        found = False
        if word != "":
          for scan in ctx.guild.text_channels:
            if word in scan.name:
              channel = scan.id
              found = True
          if not found: 
            channel = ctx.channel.id
        else:
          channel = ctx.channel.id
        channelset = data[0]["channels"]
        if channel in channelset:
          embed = discord.Embed(title="Blacklist | Enable Channel", description="That channel is already enabled!", color=discord.Color.red())
          await ctx.send(embed=embed)
          return
        channelset.append(channel)
        new_data = {
          "words": data[0]["words"],
          "channels": channelset
        }
        data.append(new_data)
        with open(database, "w") as f:
          json.dump(data, f, indent=4)
        del data[1]
        with open(database, "w") as f:
          json.dump(data, f, indent=4)
        embed = discord.Embed(title="Blacklist | Enable Channel", description=f"Enabled blacklist filtering on <#{channel}>", color=14957195)
        await ctx.send(embed=embed)
        return
      if operation.lower() == "disable":
        found = False
        if word != "":
          for scan in ctx.guild.text_channels:
            if word in scan.name:
              channel = scan.id
              found = True
          if not found: 
            channel = ctx.channel.id
        else:
          channel = ctx.channel.id
        channelset = data[0]["channels"]
        if channel not in channelset:
          embed = discord.Embed(title="Blacklist | Disable Channel", description="That channel is already disabled!", color=discord.Color.red())
          await ctx.send(embed=embed)
          return
        channelset.remove(channel)
        new_data = {
          "words": data[0]["words"],
          "channels": channelset
        }
        data.append(new_data)
        with open(database, "w") as f:
          json.dump(data, f, indent=4)
        del data[1]
        with open(database, "w") as f:
          json.dump(data, f, indent=4)
        embed = discord.Embed(title="Blacklist | Disable Channel", description=f"Disabled blacklist filtering on <#{channel}>", color=14957195)
        await ctx.send(embed=embed)
        return
      else:
        embed = discord.Embed(title="Blacklist | Invalid Operation", description="Type `!blacklist` for valid operations!", color=discord.Color.red())
        await ctx.send(embed=embed)
      
    @commands.has_role("Moderator")
    @commands.command()
    async def say(self, ctx, channel: discord.TextChannel, *, message: str):
      await channel.send(message)
    
    @commands.has_role("Moderator")
    @commands.command()
    async def embed(self, ctx, channel: discord.TextChannel, title: str, *, message: str = "none"):
      if message != "none":
        embed = discord.Embed(title=title, description=message, color=14957195)
      else:
        embed = discord.Embed(title=title, color=14957195)
      await channel.send(embed=embed)

def setup(bot):
  bot.add_cog(Admin(bot))
