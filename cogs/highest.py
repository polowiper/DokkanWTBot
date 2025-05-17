import json
import os

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import *


class HighestPace(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(
        name="highest", description="Show the highest pace of a person was."
    )  # A command to show what the highest pace of a person was (it was in the TODO so I guess someone asked for it)
    @app_commands.describe(
        identifier="The identifier of the player you want to see the highest pace of."
    )
    async def highest(self, ctx, identifier: str = None):
        try:
            await ctx.response.defer()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update == None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())
            if identifier is None:
                user_id = str(ctx.user.id)
                identifier = discord_users.get(user_id)
                if identifier is None:
                    await ctx.followup.send(
                        "You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)"
                    )
                    return
            player = find_player(players, identifier)
            if player is None:
                await ctx.followup.send(
                    f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)'
                )
                return
            paces = player.get("wins_pace")
            highest_pace = 0
            for i in paces:
                if i > highest_pace:
                    highest_pace = i
            # await ctx.send(highest_pace)
            embed = discord.Embed(
                title=f"{player['name']}'s highest pace",
                description=f"The highest pace you've had was **{highest_pace}**.",
                color=discord.Color.green(),
            )

            await ctx.followup.send(embed=embed)
        except Exception as e:
            self.bot.error(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo (@polowiper) 2 fix plz")


async def setup(bot):
    await bot.add_cog(HighestPace(bot))
