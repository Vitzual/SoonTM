import discord
import asyncio
import random
import json
from discord.ext import commands, tasks
from discord.utils import get
from collections.abc import Sequence

class Tickets(commands.Cog, name="Tickets"):
    """Ticket related commands"""
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Tickets(bot))