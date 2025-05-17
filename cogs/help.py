import asyncio
import os
import random
import time
import typing
from datetime import datetime, timedelta
from os.path import exists

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import view
from discord.utils import get

bot = None


# Function pour avoir la desc de l'embed selon le nom de la commande qu'on veut afficher la page (pas tres fr mais blc)
def gen_desc(command_name):
    cmd = bot.tree.get_command(command_name)
    # pas de alias pour les slash command je suis tres bete
    # cmd_aliases_text = "`"+ '`, `'.join(cmd.aliases)+"`" if cmd.aliases is not None else ""
    # cmd_aliases_text = f"- _Aliases:{cmd_aliases_text}_\n\n" if cmd_aliases_text else "\n\n"
    cmd_desc_text = f"\n\n**Description:** \n\n⠀⠀⠀⠀_{help_texts[command_name]}_\n\n"
    desc_text = f"**{command_name.upper()}**{cmd_desc_text}"
    return desc_text


# Menu DropDown 😎
class Dropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(
                label=command.name, description=f"Help for /{command.name}"
            )
            for command in list(bot.tree.get_commands())
        ]

        super().__init__(
            placeholder="Choose the command ...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"Help for {self.values[0]}", description=gen_desc(self.values[0])
            ),
            view=DropdownView(),
        )


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())


# Help texts
help_texts = {
    "max": "This command computes the theoretical maximum of points (or wins) the player can get in the "
    "tournament. It will depends on the highest pace achieved by the player, the number of hours "
    "remaining, and the points earned by the player. If possible, the command will add a graphic to "
    "help visualize how to achieved maximum wins/points.",
    "pace": "This command computes the current pace of the player. As the leaderboard updates itself every 15 "
    "minutes, the pace is computed by taking the difference between the current points/wins 15 minutes",
    "target": "This command computes the minimum pace need to reach a goal of points. As explained in the "
    "command, the minimum pace depends on your current points, your goal, the time left and your "
    "average points/wins ratio.",
    "when": "This commands takes a goal and a pace and a pace_type and computes the estimated time of when the player will reach the goal.",
    "highest": "This command simply return the highest pace achieved by the player. If you are not in the top "
    "100, your pace won't appeared in the leaderboard so the bot will not record it.",
    "leaderboard": "This command shows the leaderboard of the tournament. The leaderboard is updated every 15 "
    "minutes (8:30, 8:45, 9:00, ...) so the data may not be up to date when you type /leaderboard.",
    "gap": "This command computes the gap between the player, the player above and the player below. The gap "
    "is computed by taking the difference between the player's points/wins and the player above/below."
    "It will also say if the player above is farming faster than you, in which case the bot will "
    "computes an estimation when the player will go beyond the player above him. If not it will say "
    "that he is faster.",
    "seed": "This command shows the seed of the player. The seed is the points/wins ratio. If possible, a "
    "graph will be displayed. ",
    "compare": "This command compares the points/wins/ranks of several players. By typing "
    "/compare type:points users:Discord BabaYaga Lotad, the bot will return a graph with the points"
    " of the 3 players (if their data is available). ",
    "ranking": "This command shows the ranking of the player. The bot simply track the player's ranking every "
    "15 minutes (if the player is in the top 100), and send a graph with these information.",
    "points": "This command shows the points of the player. The bot simply track the player's points every 15 "
    "minutes (if the player is in the top 100), and send a graph with these information.",
    "wins": "This command shows the wins of the player. The bot simply track the player's wins every 15 "
    "minutes (if the player is in the top 100), and send a graph with these information.",
    "link": "This command allows you to link your discord ID to your in-game name. By typing /link name:your_name, "
    "the bot know who you are and will be able to track your data. If you want to change your name, "
    "simply type /link name:new_name. The bot will ask you if you want to update it.",
    "gap": "This command shows the gap between you and the players under and above you (in terms of ranks)."
    "It also shows the difference of gap between 2 resets telling you if you're faster or slower than your opponents",
    "bulk": "A pretty ugly command that gives you a bunch of data in bulk (might make something out of it later on idk)",
    "help": "Show this page.",
}


# Autocompletion help
async def autocompletion_help(
    interaction: discord.Interaction, current: str
) -> typing.List[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=a.name, value=a.name)
        for a in list(bot.tree.get_commands())
    ]
    return choices


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name="help", description="Shows the help menu.")
    @app_commands.describe(cmd="The command to get help on.")
    @app_commands.autocomplete(cmd=autocompletion_help)
    async def help(self, ctx, cmd: str = None):
        await ctx.response.defer()
        embed = discord.Embed(title="Help Menu")
        try:
            if cmd is None:
                desc = "Use `/help <command>` to get more info on a command. Available commands:\n"
                for command in list(self.bot.tree.get_commands()):  # Set to List
                    # embed.add_field(name=command.name, value=command.description, inline=False)
                    desc += f"\n- **/{command.name}**: _{command.description}_"
                embed.description = desc
                await ctx.followup.send(embed=embed)
            else:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title=f"Help for {cmd}", description=gen_desc(cmd)
                    ),
                    view=DropdownView(),
                )
        except Exception as e:
            log_message(f"An Error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo (@polowiper) 2 fix plz")


async def setup(bot):
    await bot.add_cog(Help(bot))
