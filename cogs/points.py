import typing
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from render import render

from cogs.utils import *


class PlayerSelectView(discord.ui.View):

    def __init__(self, players, ctx, update, borders, callback):
        super().__init__()
        self.ctx = ctx
        self.update = update
        self.borders = borders
        self.callback = callback

        select = discord.ui.Select(
            placeholder="Select a player...",
            options=[
                discord.SelectOption(
                    label=f"#{player["ranks"][-1]}:{player["name"]}", value=str(index)
                )
                for index, player in enumerate(players)
            ],
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.user.id:
            await interaction.response.send_message(
                "You're not allowed to select this.", ephemeral=True
            )
            return

        selected_index = int(interaction.data["values"][0])
        selected_player = self.callback(selected_index)
        await interaction.message.delete()
        await self.ctx.cog.process_player(
            self.ctx, selected_player, self.update, self.borders
        )


class PointsCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def autocomplete_borders(
        self, interaction: discord.Interaction, current: str
    ) -> typing.List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name="Yes", value="1"),
            app_commands.Choice(name="No", value="0"),
        ]

    @app_commands.command(name="points", description="Show the points of a player.")
    @app_commands.describe(
        identifier="The identifier of the player you want to see the points of.",
        rank="If you wish to search a player by rank instead.",
        borders="Whether or not you want to see borders on the graph",
    )
    @app_commands.autocomplete(borders=autocomplete_borders)
    async def points(
        self, ctx, identifier: str = None, rank: str = None, borders: str = None
    ):
        try:
            await ctx.response.defer()
            conn = load_db_data()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update is None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())

            if identifier is None:
                if rank is None:
                    user_id = str(ctx.user.id)
                    identifier = discord_users.get(user_id)
                    if identifier is None:
                        await ctx.followup.send(
                            "You did not provide a Dokkan name/ID and your Discord account isn't linked. Please provide an identifier or link your account (/link)."
                        )
                        return
                else:
                    identifier = find_rank(conn, rank)

            players = find_player(conn, identifier)

            if not players:
                await ctx.followup.send(
                    f'Player with name, ID, or rank "{identifier}" not found. (not in the top 10,000 ???)'
                )
                return

            if isinstance(players, list) and len(players) > 1:
                if len(players) >= 25:
                    await ctx.followup.send(
                        "Too many users found with a matching name. Please be more precise."
                    )
                    return

                view = PlayerSelectView(
                    players, ctx, update, borders, lambda idx: players[idx]
                )
                await ctx.followup.send(
                    "Multiple players found. Please select one:", view=view
                )
                return

            player = players if isinstance(players, dict) else players[0]
            await self.process_player(ctx, player, update, borders)

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
            image_path = os.path.join(
                output_dir, player["name"].replace("$", "\\$"), "points.png"
            )

            embed = discord.Embed(
                title=f"{player['name']}'s current points",
                description=f"The current points are **{current_points:,}**.",
                color=discord.Color.red(),
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="points.png")
                embed.set_image(url=f"attachment://points.png")
                embed.add_field(
                    name="Updated at",
                    value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)",
                    inline=False,
                )
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(
                    name="Updated at",
                    value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)",
                    inline=False,
                )
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(
                f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top 10,000 and that's a skill issue as well)"
            )


async def setup(bot):
    await bot.add_cog(PointsCommand(bot))
