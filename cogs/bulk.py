import os
import typing
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Select, View
from render import bulk_render

from cogs.utils import *

AVAILABLE_PARAMS = [
    "ranks",
    "wins",
    "points",
    "wins_pace",
    "points_pace",
    "points_wins",
    "max_points",
    "max_wins",
]


class PlayerSelect(Select):
    def __init__(self, players, ctx, update, selected_params):
        self.ctx = ctx
        self.players = players
        self.update = update
        self.selected_params = selected_params

        options = [
            discord.SelectOption(
                label=f"#{player['ranks'][-1]}:{player['name']}",
                value=str(index),  # Adjusted label format
            )
            for index, player in enumerate(players)
        ]
        super().__init__(placeholder="Select a player...", options=options)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.ctx.user.id:
            await interaction.response.send_message(
                "You cannot select a player for this command.", ephemeral=True
            )
            return

        await interaction.response.defer()
        selected_index = int(self.values[0])
        player = self.players[selected_index]
        await self.view.process_bulk(
            self.ctx, player, self.update, self.selected_params, interaction
        )


class PlayerSelectView(View):
    def __init__(self, players, ctx, update, selected_params):
        super().__init__()
        self.add_item(PlayerSelect(players, ctx, update, selected_params))

    async def process_bulk(
        self, ctx, player, update, selected_params, interaction=None
    ):
        bulk_render([player], output_dir, selected_params)
        image_path = os.path.join(
            output_dir,
            player["name"].replace("$", "\\$"),
            f"bulk_{'_'.join(selected_params)}.png",
        )
        embed = discord.Embed(
            title=f"Bulk Summary ({', '.join(selected_params)})",
            description="ab lablalbla",
            color=discord.Color.purple(),
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="bulk.png")
            embed.set_image(url=f"attachment://bulk.png")
            embed.add_field(
                name="Updated at",
                value=f"<t:{int(update.timestamp())}:f>  (<t:{int(update.timestamp())}:R>)",
                inline=False,
            )
            if interaction:
                await interaction.followup.send(file=file, embed=embed)
            else:
                await ctx.followup.send(file=file, embed=embed)
        else:
            if interaction:
                await interaction.followup.send(embed=embed)
            else:
                await ctx.followup.send(embed=embed)


class BulkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    async def bulk_param_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> typing.List[app_commands.Choice[str]]:
        selected_params = [p.strip() for p in current.split(",") if p.strip()]
        available_remaining = [
            param for param in AVAILABLE_PARAMS if param not in selected_params
        ]
        choices = []
        for param in available_remaining:
            suggestion = current
            if suggestion and not suggestion.endswith(","):
                suggestion += ","
            suggestion += param
            choices.append(app_commands.Choice(name=suggestion, value=suggestion))

        return choices

    @app_commands.command(name="bulk", description="get the bulk infos of a player")
    @app_commands.describe(
        identifier="the identifier of the player you want to see the bulk info of.",
        params="the parameters you want to include in the bulk info (e.g., points, wins). you can select multiple.",
        rank="If you wish to provide a rank instead of an identifier",
    )
    @app_commands.autocomplete(params=bulk_param_autocomplete)
    async def bulk(
        self,
        ctx,
        identifier: str = None,
        params: str = "wins_pace,wins,ranks,points_wins",
        rank: str = None,
    ):
        try:
            await ctx.response.defer()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update is None:
                update = datetime.fromisoformat("2005-03-30").replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            conn = load_db_data()
            if identifier is None:
                if rank is None:
                    user_id = str(ctx.user.id)
                    identifier = discord_users.get(user_id)
                    if identifier is None:
                        await ctx.followup.send(
                            "You did not provide a Dokkan name/ID and your Discord account isn't linked to any. Please provide an identifier or link your Discord account (/link)."
                        )
                        return
                else:
                    identifier = find_rank(conn, rank)

            players = find_player(conn, identifier)

            if not players:
                await ctx.followup.send(
                    f'player with name or id "{identifier}" not found. (not in the top 10,000?)'
                )
                return

            selected_params = []
            if params:
                selected_params = [p.strip() for p in params.split(",")]
                invalid_params = [
                    p for p in selected_params if p not in AVAILABLE_PARAMS
                ]
                if invalid_params:
                    await ctx.followup.send(
                        f"invalid parameters provided: {', '.join(invalid_params)}. available parameters are: {', '.join(AVAILABLE_PARAMS)}"
                    )
                    return
                if len(selected_params) < 2:
                    await ctx.followup.send(
                        "Please provide at least 2 parameters, if you only want to use one then just use the associated function"
                    )
                    return
            else:
                await ctx.followup.send(
                    "please specify at least two parameters to display."
                )
                return

            if isinstance(players, list) and len(players) > 1:
                if len(players) >= 25:
                    await ctx.followup.send(
                        "too many users found with a matching name. please be more precise."
                    )
                    return
                await ctx.followup.send(
                    "multiple players found. please select one:",
                    view=PlayerSelectView(players, ctx, update, selected_params),
                )
                return

            player = players if isinstance(players, dict) else players[0]
            bulk_render([player], output_dir, selected_params)
            image_path = os.path.join(
                output_dir,
                player["name"].replace("$", "\\$"),
                f"bulk_{'_'.join(selected_params)}.png",
            )
            embed = discord.Embed(
                title=f"bulk summary ({', '.join(selected_params)})",
                description="ab lablalbla",
                color=discord.Color.purple(),
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="bulk.png")
                embed.set_image(url=f"attachment://bulk.png")
                embed.add_field(
                    name="updated at",
                    value=f"<t:{int(update.timestamp())}:f>  (<t:{int(update.timestamp())}:R>)",
                    inline=False,
                )
                await ctx.followup.send(file=file, embed=embed)
            else:
                await ctx.followup.send(embed=embed)

        except Exception as e:
            self.bot.log_message(f"an error occurred: {e}")
            await ctx.followup.send(f"me no worki lol ask polo 2 fix plz")


async def setup(bot):
    await bot.add_cog(BulkCommand(bot))
