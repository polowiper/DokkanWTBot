import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render
import os
import typing
class PlayerSelect(discord.ui.Select):
    def __init__(self, players, ctx, borders, update):
        self.ctx = ctx
        self.players = players
        self.borders = borders
        self.update = update

        options = [
            discord.SelectOption(label=player["name"], value=str(index))
            for index, player in enumerate(players)
        ]
        super().__init__(placeholder="Select a player...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_index = int(self.values[0])
        player = self.players[selected_index]
        wins_data = player.get("wins")

        if wins_data:
            render([player], output_dir, "wins", border=self.borders)
            current_wins = wins_data[-1]
            image_path = os.path.join(output_dir, player["name"], "wins.png")

            embed = discord.Embed(
                title=f"{player['name']}'s Current Wins",
                description=f"The current wins are **{current_wins:,}**.",
                color=discord.Color.brand_red()
            )
            embed.add_field(name="Updated at", value=f"<t:{int(self.update.timestamp())}:f> (<t:{int(self.update.timestamp())}:R>)", inline=False)

            if os.path.exists(image_path):
                file = discord.File(image_path, filename="wins.png")
                embed.set_image(url="attachment://wins.png")
                await interaction.response.edit_message(content=None, embed=embed, attachments=[file], view=None)
            else:
                await interaction.response.edit_message(content=None, embed=embed, view=None)
        else:
            await interaction.response.edit_message(content=f"No data available for wins.", view=None)


class PlayerSelectView(discord.ui.View):
    def __init__(self, players, ctx, borders, update):
        super().__init__()
        self.add_item(PlayerSelect(players, ctx, borders, update))


class WinsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot
    async def autocomplete_borders(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name="Yes", value="1"),
            app_commands.Choice(name="No", value="0")
        ]
        return choices

    @app_commands.command(name='wins', description="Show the wins of a player.")
    @app_commands.describe(identifier="The identifier of the player you want to see the wins of.", borders="Whether or not you want to see the borders on your graphs")
    @app_commands.autocomplete(borders=autocomplete_borders)
    async def wins(self, ctx, identifier: str = None, borders:str=None):
        try:
            await ctx.response.defer()
            conn = load_db_data()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if borders == "1":
                borders = find_borders(conn, 100)
            else:
                borders = None
            if update is None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())

            if identifier is None:
                user_id = str(ctx.user.id)
                identifier = discord_users.get(user_id)
                if identifier is None:
                    await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any. Please provide an identifier or link your Discord account (/link).")
                    return

            players = find_player(conn, identifier)

            if not players:
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (Not in the top 10,000?)')
                return

            if isinstance(players, list) and len(players) > 1:
                if len(players) >= 25:
                    await ctx.followup.send("Too many users found with a matching name. Please be more precise.")
                    return
                await ctx.followup.send("Multiple players found. Please select one:", view=PlayerSelectView(players, ctx, borders, update))
                return

            player = players if isinstance(players, dict) else players[0]
            wins_data = player.get("wins")

            if wins_data:
                render([player], output_dir, "wins", border=borders)
                current_wins = wins_data[-1]
                image_path = os.path.join(output_dir, player["name"], "wins.png")

                embed = discord.Embed(
                    title=f"{player['name']}'s Current Wins",
                    description=f"The current wins are **{current_wins:,}**.",
                    color=discord.Color.brand_red()
                )
                embed.add_field(name="Updated at", value=f"<t:{int(update.timestamp())}:f> (<t:{int(update.timestamp())}:R>)", inline=False)

                if os.path.exists(image_path):
                    file = discord.File(image_path, filename="wins.png")
                    embed.set_image(url="attachment://wins.png")
                    await ctx.followup.send(file=file, embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.followup.send("No data available for wins. Either fetch failed or you're not in the top 10,000.")
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send("Me no worki lol ask Polo 2 fix plz")


async def setup(bot):
    await bot.add_cog(WinsCommand(bot))
