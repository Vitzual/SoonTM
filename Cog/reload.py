# This is the reload module. Please don't touch anything in here
# as it's very fragile and can easily get it's feelings broken if you're
# mean to it. (also it's the most useful Cog by far)

import discord
import asyncio
from discord.ext import commands, tasks
from discord.ext.commands import Bot

class Reload(commands.Cog, name="Reload"):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("Moderator")
    @commands.command()
    async def reload(self, ctx, module: str):
        try:
            if module.startswith("Cog."):
                self.bot.reload_extension(module)
            else:
                self.bot.reload_extension(f"Cog.{module}")
        except Exception as e:
            print(e)
            print()
            embed = discord.Embed(title="Module error", description=f"Oops! That module doesn't exist.\n**Error:** {e}", color=14957195)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Module reloaded", description="The module was reloaded successfully", color=14957195)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Reload(bot))
