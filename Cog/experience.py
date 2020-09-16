import discord
import random
import json
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

                exp = scan["xp"]
                rank = self.bot.get_role(scan["current"])
                ranks="Axiiom/xp_ranks.json"
                with open(ranks) as f:
                    rankdata = json.load(f)
                threshold = 0
                for level in rankdata:
                    if level["rank_id"] == rank.id:
                        total = level["threshold"]
                embed = discord.Embed(title="Rank Overview | {user.name}", description="**Rank:** {rank.name}\n**Rank Progress:** {exp}xp/{threshold}", color=14957195)
                await ctx.send(embed=embed)
                return
        embed = discord.Embed(title=f"Rank Overview | {user.name}", description="**Rank:** Common Member\n**Rank Progress:** 0xp/1000", color=14957195)
        await ctx.send(embed=embed)
        
        
        
def setup(bot):
    bot.add_cog(Experience(bot))