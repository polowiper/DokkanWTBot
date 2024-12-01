import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render
import typing
class MaxCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    #Autocompletion max
    async def autocompletion_type_max(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name=a, value=a)
            for a in ["wins", "points"]
            ]
        return choices

    @app_commands.command(name="max", description="Show the maximum points or wins of a player.")
    @app_commands.describe(type="The type of maximum you want to see. Either 'points' or 'wins'.", identifier="The identifier of the player you want to see the maximum of.")
    @app_commands.autocomplete(type=autocompletion_type_max)
    async def max_(self, ctx, type: str = "points", identifier: str = None):
        try:
            await ctx.response.defer()
            # check type
            if type not in ["wins", "points"]:
                await ctx.followup.send("Please provide a valid type. Either 'points' or 'wins'.")
                return
            conn = load_db_data()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update == None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())
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
            maximum = player.get(f"max_{type}")
            if maximum:
                render([player], output_dir, f"max_{type}")
                current_max = maximum[-1] 
                image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), f'max_{type}.png')

                embed = discord.Embed(
                    title=f"{player['name']}'s maximum {type} achieveable",
                    description=f"Your current max is **{round(current_max, 0):,} {type}**.",
                    color=discord.Color.green()
                )
                if os.path.exists(image_path):
                    file = discord.File(image_path, filename=f"max_{type}.png")
                    embed.set_image(url=f"attachment://max_{type}.png")
                    embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)

                    await ctx.followup.send(file=file, embed=embed)
                else:

                    await ctx.followup.send(embed=embed)
                    embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
            else:
                await ctx.followup.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
        except Exception as e:
            bot.self.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")


async def setup(bot):
    await bot.add_cog(MaxCommand(bot))

