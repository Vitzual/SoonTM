import discord
import random
import json
from discord.ext import commands, tasks
from discord.utils import get

class Economy(commands.Cog, name="Economy"):
    """Economy commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def guags(self, ctx, operation:str = "", user: discord.Member = None, amount: int = 0):
      database="Axiiom/user_economy.json"
      if user:
        if user.id == 749435207160954880:
          await ctx.send("I sort of uh, lost my purse. Unfortunately I can't hold guags because of that ;(")
          return
      if operation == "":
        admin = False
        for scan in ctx.author.roles:
          if scan.name == "Moderator":
            embed = discord.Embed(title=f"Guags Economy | Command List", description="Earn guags from games and dungeons!\n\n**View guags:** `!guags view`\nShows the amount of guags you have\n\n**View others guags:** `!guags view [user]`\nShows the amount of guags that user owns\n\n**View leaderboard:** `!guags leaderboard`\nDisplay the wealthiest of wealthy members\n\n**Gift guags:** `!guags gift [user] [amount]`\nGift user x amount of guags (Taxes may apply)\n\n**Add guags:** `!guags add [user] [amount]`\nAdds x amount of guags to a user\n\n**Remove guags:** `!guags remove [user] [amount]`\nRemoves x amount of guags from a user", color=14957195)
            admin = True
        if not admin:
          embed = discord.Embed(title=f"Guags Economy | Command List", description="Earn guags from games and dungeons!\n\n**View guags:** `!guags view`\nShows the amount of guags you have\n\n**View others guags:** `!guags view [user]`\nShows the amount of guags that user owns\n\n**View leaderboard:** `!guags leaderboard`\nDisplay the wealthiest of wealthy members\n\n**Gift guags:** `!guags gift [user] [amount]`\nGift user x amount of guags (Taxes may apply)", color=14957195)
        embed.set_thumbnail(url="https://i.ibb.co/rFMdyLL/Untitled-2.png")
        await ctx.send(embed=embed)
        return
      elif operation == "top" or operation == "leaderboards" or operation == "lb" or operation == "leaderboard":
        with open(database) as f:
          data = json.load(f)
        datboi = []
        for scan in data:
          datboi.append([scan["balance"],scan["user_id"]])
        datboi.sort(reverse=True)
        index = 0
        description = ""
        for scan in datboi:
          user = self.bot.get_user(datboi[index][1])
          if user is not None:
            if user.id == ctx.author.id:
              description = description + f"**{index+1}) {user.name} [{str(datboi[index][0])} guags]**\n"
              index+=1
            else:
              description = description + f"**{index+1})** {user.name} [" + str(datboi[index][0]) + " guags]\n"
              index+=1
        embed = discord.Embed(title="Guags Economy | Leaderboards", description=description, color=14957195)
        await ctx.send(embed=embed)           
      elif operation == "view":
        if user is None:
          user = ctx.author
        with open(database) as f:
          data = json.load(f)
        for scan in data:
          if scan["user_id"] == user.id:
            balance = scan["balance"]
            if balance == 1:
              embed = discord.Embed(title=f"Guags Economy | {user.name}'s Balance", description=f"{user.name} has 1 guag in their purse.", color=14957195)
            else:
              embed = discord.Embed(title=f"Guags Economy | {user.name}'s Balance", description=f"{user.name} has {balance} guags in their purse.", color=14957195)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=f"Guags Economy | {user.name}'s Balance", description=f"{user.name} has 0 guags in their purse.", color=14957195)
        await ctx.send(embed=embed)
        return
      elif operation == "add":
        admin = False
        for scan in ctx.author.roles:
          if scan.name == "Moderator":
            admin = True
        if admin:
          if user is None:
            embed = discord.Embed(title=f"Guags Economy | Add Guags", description=f"Please specify a valid user!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
          elif amount <= 0:
            embed = discord.Embed(title=f"Guags Economy | Add Guags", description=f"Please specify a valid amount to give!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
          else:
            with open(database) as f:
              data = json.load(f)
            index=0
            for scan in data:
              if scan["user_id"] == user.id:
                total = int(scan["balance"]+amount)
                new_data = {
                  "user_id": user.id,
                  "balance": total
                }
                del data[index]
                data.append(new_data)
                with open(database, "w") as f:
                  json.dump(data, f, indent=4)
                embed = discord.Embed(title=f"Guags Economy | Add Guags", description=f"Added {amount} guags to {user.name}\n**New balance:** {total}", color=14957195)
                await ctx.send(embed=embed)
                return
              index+=1
            new_data = {
              "user_id": user.id,
              "balance": amount
            }
            data.append(new_data)
            with open(database, "w") as f:
              json.dump(data, f, indent=4)
            embed = discord.Embed(title=f"Guags Economy | Add Guags", description=f"Added {amount} guags to {user.name}\n**New balance:** {amount}", color=14957195)
            await ctx.send(embed=embed)
            return
      elif operation == "remove":
        admin = False
        for scan in ctx.author.roles:
          if scan.name == "Moderator":
            admin = True
        if admin:
          if user is None:
            embed = discord.Embed(title=f"Guags Economy | Remove Guags", description=f"Please specify a valid user!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
          elif amount <= 0:
            embed = discord.Embed(title=f"Guags Economy | Remove Guags", description=f"Please specify a valid amount to give!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
          else:
            with open(database) as f:
              data = json.load(f)
            index=0
            for scan in data:
              if scan["user_id"] == user.id:
                total = int(scan["balance"]-amount)
                if total < 0:
                  embed = discord.Embed(title=f"Guags Economy | Remove Guags", description=f"Users cannot have negative guags!", color=discord.Color.red())
                  await ctx.send(embed=embed)
                  return
                new_data = {
                  "user_id": user.id,
                  "balance": total
                }
                del data[index]
                data.append(new_data)
                with open(database, "w") as f:
                  json.dump(data, f, indent=4)
                embed = discord.Embed(title=f"Guags Economy | Remove Guags", description=f"Removed {amount} guags from {user.name}\n**New balance:** {total}", color=14957195)
                await ctx.send(embed=embed)
                return
              index+=1
      elif operation == "gift":
        if user is None or user == ctx.author:
          embed = discord.Embed(title=f"Guags Economy | Gift Guags", description=f"Please specify a valid user!", color=discord.Color.red())
          await ctx.send(embed=embed)
          return
        elif amount <= 1:
          if amount == 1:
            embed = discord.Embed(title=f"Guags Economy | Gift Guags", description=f"Please specify a valid amount over 1 guag!\n\n**Why can't I gift 1 guag?**\nSince taxes use whole numbers, tax on 1 guag\nwould be 0, meaning you could evade taxes and\npossibly be caught for tax fraud down the road.", color=discord.Color.red())
          else:
            embed = discord.Embed(title=f"Guags Economy | Gift Guags", description=f"Please specify a valid amount over 1 guag!", color=discord.Color.red())
          await ctx.send(embed=embed)
          return
        else:
          with open(database) as f:
            data = json.load(f)
          index=0
          for scan in data:
            if scan["user_id"] == ctx.author.id:
              total = int(scan["balance"]-amount)
              if total < 0:
                embed = discord.Embed(title=f"Guags Economy | Gift Guags", description=f"You cannot have negative guags!", color=discord.Color.red())
                await ctx.send(embed=embed)
                return
              new_data = {
                "user_id": ctx.author.id,
                "balance": total
              }
              break
            index+=1
          embed = discord.Embed(title=f"Guags Economy | Gift Guags", description=f":warning: **Guaguag takes 15% of all gifts**\nThis means you'll only gift {int(amount*0.85)} guags\n\nTo proceed, type `confirm`", color=14957195)
          await ctx.send(embed=embed)
          def check(m):
            return m.author == ctx.author
          try:
            a = await self.bot.wait_for('message', check=check, timeout=20.0)
          except:
            embed = discord.Embed(title="Guags Economy | Gift Guags", description="You took too long to reply!", color=discord.Color.red())
            await ctx.channel.send(embed=embed)
            return
          confirm = str(a.content.lower())
          if confirm != "confirm":
            embed = discord.Embed(title=f"Guags Economy | Gift Guags", description=f"You did not confirm properly!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
          del data[index]
          data.append(new_data)
          with open(database, "w") as f:
            json.dump(data, f, indent=4)
          bypass = False
          index = 0
          for scan in data:
            if scan["user_id"] == user.id:
              balance = (scan["balance"] + int(amount*0.85))
              new_data = {
                "user_id": user.id,
                "balance": balance
              }
              del data[index]
              bypass = True
            index+=1
          if not bypass:
            balance = int(amount*0.85)
            new_data = {
              "user_id": user.id,
              "balance": balance
            }
          data.append(new_data)
          with open(database, "w") as f:
            json.dump(data, f, indent=4)
          embed = discord.Embed(title=f"Guags Economy | Gift Guags", description=f"Gifted {amount} guags to {user.name}\n\n**Their balance:** {balance} guags\n**Your balance:** {total} guags", color=14957195)
          await ctx.send(embed=embed)
          return
      else:
        embed = discord.Embed(title=f"Guags Economy | Invalid Operation", description=f"View valid operations using `!guags`", color=discord.Color.red())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))