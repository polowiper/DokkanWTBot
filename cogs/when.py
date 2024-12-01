import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render
import typing
class WhenCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot
    #Autocompletion when
    async def autocompletion_type_goal(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name=a, value=a)
            for a in ["wins", "points"]
            ]
        return choices

    @app_commands.command(name="when", description="Show the estimated time of when a player will reach a goal.")
    @app_commands.describe(goal="The goal you want to reach.", identifier="The identifier of the player you want to see the estimated time of.")
    @app_commands.autocomplete(goal_type=autocompletion_type_goal)
    async def when(self, ctx, goal: str, goal_type: str = "points", pace: int = 0, identifier: str = None):
        try:
            await ctx.response.defer()
            if pace == 0:
                await ctx.followup.send("Please provide a pace.")
                return
            num = {
                "m": 1000000,
                "b": 1000000000,
                "k": 1000
            }
            goal = int(goal[:-1]) * num[goal[-1]]
            conn = load_db_data()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update == None:
                self.bot.log_message("No update time found, setting to default")
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())
                end = update
                start = update
                
            if identifier is None:
                user_id = str(ctx.user.id)
                identifier = discord_users.get(user_id)
                if identifier is None:
                    await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                    return

            player = find_player(conn, identifier)

            if player is None:
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return
            
            if goal_type == "points":
                player_points = player["points"][-1]
                goal_points = int(goal)
                if goal_points <= player_points:
                    await ctx.followup.send("Please provide a goal higher than your current points.")
                    return
                req_points = goal_points - player_points
                req_hours = req_points / pace
                final_timestamp = (update + timedelta(hours=req_hours)).timestamp()
                req = req_points
            
            elif goal_type == "wins":
                player_wins = player["wins"][-1]
                goal_wins = int(goal)
                if goal_wins < player_wins:
                    await ctx.followup.send("Please provide a goal higher than your current wins.")
                    return
                req_wins = goal_wins - player_wins
                req_hours = req_wins / pace
                final_timestamp = (update + timedelta(hours=req_hours)).timestamp()
                req = req_wins
            if final_timestamp > end.timestamp():
                await ctx.followup.send("You can't reach this goal in the future.... L")
                return
            embed = discord.Embed(
                title=f"{player['name']}'s estimated time to reach {goal:,} points",
                description=f"You need to reach **{req:,}** points in **{round(req_hours, 2):,}** hours to reach your goal.",
                color=discord.Color.green()
            )
            embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)

            await ctx.followup.send(embed=embed)
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(WhenCommand(bot))

