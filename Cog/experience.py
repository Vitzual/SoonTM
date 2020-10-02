import discord
import random
import json
import math
from discord.ext import commands, tasks
from discord.utils import get

class Experience(commands.Cog, name="Experience"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def rank(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        database="Axiiom/user_ranks.json"
        with open(database) as f:
            data = json.load(f)
        for scan in data:
            if scan["user_id"] == user.id:
                exp = check_cur(scan["xp"])
                rank = get(ctx.guild.roles, id=scan["rank"])
                embed = discord.Embed(title=f"Rank Overview | {user.name}", description=f"**Rank:** {rank.name}\n**Level:** {check_level(exp)} ({exp}xp / {check_req(exp)}xp)", color=14957195)
                await ctx.send(embed=embed)
                return
        embed = discord.Embed(title=f"Rank Overview | {user.name}", description="**Rank:** Common Member\n**Level:** 0", color=14957195)
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Experience(bot))
    
def check_level(a):
    return int(0.16 * math.sqrt(a))

def check_req(a):
    return int(math.pow(((int(0.16 * math.sqrt(a))+1)/0.16),2))

def check_cur(a):
    return int(0.16 * math.sqrt(a))

def check_rank(a):
    database = "Axiiom/user_ranks.json",0
    with open(database) as f:
        ranks = json.load(f)
    for scan in ranks:
        if scan["user_id"] == a:
            return scan["rank"]
    return 568614562526396427