import json
import os

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import *


class FetchCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(
        name="fetchcount", description="Counts the number of fetches done by the bot.."
    )  # A command to show what the highest pace of a person was (it was in the TODO so I guess someone asked for it)
    async def fetchcount(self, ctx):
        await ctx.response.defer()

        def count_file(directory):
            count = 0
            for file in os.listdir(directory):
                if file.endswith(".json"):
                    count += 1
            return count

        try:
            await ctx.followup.send(count_file("fetches"))
        except Exception as e:
            self.bot.error(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo (@polowiper) 2 fix plz")


async def setup(bot):
    await bot.add_cog(FetchCount(bot))
