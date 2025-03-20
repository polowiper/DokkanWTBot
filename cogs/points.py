import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render
import typing
class PointsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot
    async def autocomplete_borders(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name="Yes", value="1"),
            app_commands.Choice(name="No", value="0")
        ]
        return choices

    @app_commands.command(name='points', description="Show the points of a player.")
    @app_commands.describe(identifier="The identifier of the player you want to see the points of.", borders="Whether or not you want to see the borders on the graph")
    @app_commands.autocomplete(borders=autocomplete_borders)
    async def points(self, ctx, identifier: str = None, borders: str = None):
        try:
            await ctx.response.defer()
            conn = load_db_data()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update is None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())

            if identifier is None:
                user_id = str(ctx.user.id)
                identifier = discord_users.get(user_id)
                if identifier is None:
                    await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any. Please provide an identifier or link your Discord account (/link)")
                    return

            players = find_player(conn, identifier)
            
            if not players:
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top 10,000 ???)')
                return

            if isinstance(players, list):
                if len(players) >= 25:
                    await ctx.followup.send("Too many users found with a matching name. Please be more precise.")
                    return
                
                view = discord.ui.View()
                
                async def select_callback(interaction: discord.Interaction):
                    selected_player = next(p for p in players if p["name"] == interaction.data["values"][0])
                    await interaction.message.delete()
                    await self.process_player(ctx, selected_player, update, borders)
                
                select = discord.ui.Select(
                    placeholder="Select the correct player",
                    options=[discord.SelectOption(label=p["name"], value=p["name"]) for p in players]
                )
                select.callback = select_callback
                view.add_item(select)
                await ctx.followup.send("Multiple players found, please select one:", view=view)
                return
            
            await self.process_player(ctx, players, update, borders)
        
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send("Me no worki lol ask Polo 2 fix plz")
    
    async def process_player(self, ctx, player, update, borders=None):
        conn = load_db_data()
        if borders == "1":
    
            borders = find_borders(conn, 100)
        else:
            borders = None
        points_data = player.get("points")
        
        if points_data:
            render([player], output_dir, "points", border=borders)
            current_points = points_data[-1]
            image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), 'points.png')
            
            embed = discord.Embed(
                title=f"{player['name']}'s current points",
                description=f"The current points are **{current_points:,}**.",
                color=discord.Color.red()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="points.png")
                embed.set_image(url=f"attachment://points.png")
                embed.add_field(name="Updated at", value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(name="Updated at", value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top 10,000 and that's a skill issue as well)")

async def setup(bot):
    await bot.add_cog(PointsCommand(bot))