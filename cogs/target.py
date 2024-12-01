import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render

class TargetCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name="target", description="Show the pace needed to reach a goal.")
    @app_commands.describe(goal="The goal you want to reach.", identifier="The identifier of the player you want to see the pace of.")
    async def target(self, ctx, goal: str, identifier: str = None):
        try:
            await ctx.response.defer()
            # Test goal (500M --> 500000000)
            num = {
                "m": 1000000,
                "b": 1000000000,
                "k": 1000
            }
            goal = int(goal[:-1]) * num[goal[-1]]
            try:
                goal = int(goal)
            except ValueError: # l'argument fourni n'est pas un nombre
                await ctx.followup.send("Please provide a valid number as a goal.", ephemeral=True)
                return
            conn = load_db_data()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if left == None:
                await ctx.followup.send("No time left to do the calculations.")
                return
            if identifier is None:
                # cette ligne va raise un AttributeError si l'author n'est pas register, on modifie donc
                try:
                    user_id = str(ctx.user.id)
                except AttributeError as e:
                    # raise e # debug
                    await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link).")
                    return
                # tout va bien si on arrive là, on continue
                identifier = discord_users.get(user_id)
                if identifier is None: # si c'est None pour une raison ou pour une autre, même tarif c'est qu'il n'est pas register
                    await ctx.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link).")
                    return
            if goal == -1 : # devrait être useless
                await ctx.send("Please provide a goal")
                return
            player = find_player(conn, identifier)
            if player is None:
                await ctx.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return
            wins_points_ratio = player["points_wins"][-1]
            update, start, end, total, left, elapsed = time_data()
            req_pace = (goal - player["points"][-1]) / (left.days * 24 + left.seconds / 3600)
            req_wins_pace = req_pace / wins_points_ratio
            # Check si le nombre de points est plus petit que goal
            if player["points"][-1] >= goal: # plus grand, problème
                addtt = "**:warning: You already have more points than your goal, thus the pace needed is 0.**\n\n"
            else: # rien à signaler, circulez monsieur bonne journée 👮
                addtt = ""
            # await ctx.send(f"Based on your current points, your goal, the time left and your average points/wins ratio.\n You would need to have a pace of {req_wins_pace} wins/hour to be able to reach {goal} points")
            embed = discord.Embed(
                title=f"{player['name']}'s target pace",
                color=discord.Color.green(),
                description=f"{addtt}• You would need to have a pace of **{round(req_wins_pace, 2)}** wins/hour to be able to reach **{goal:,}** points.\n\n_Note : this is based on your current points, your goal, the time left and your average points/wins ratio._",
            )
            await ctx.followup.send(embed=embed)
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(TargetCommand(bot))