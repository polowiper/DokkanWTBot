import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render
import typing
class PaceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

     #Autocompletion pace
    async def autocompletion_type_pace(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name=a, value=a)
            for a in ["wins", "points"]
            ]
        return choices

    @app_commands.command(name='pace', description="Show your current pace.")
    @app_commands.describe(pace_type="The pace type you want to see. Either 'wins' or 'points'.", identifier="The identifier of the player you want to see the pace of.")
    @app_commands.autocomplete(pace_type=autocompletion_type_pace)
    async def pace(self, ctx, pace_type: str = "wins", identifier: str = None):
        try:
            await ctx.response.defer()
            # vérifier si le type est valide
            if pace_type not in ["wins", "points"]:
                await ctx.followup.send("Please provide a valid type. Either 'wins' or 'points'.")
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

            pace_type = pace_type + "_pace"
            if pace_type not in ['wins_pace', 'points_pace']:
                await ctx.followup.send(f'Invalid pace type "{pace_type}". Use "wins" or "points" ex:`!pace wins Lotad`.')
                return

            pace_data = player.get(pace_type)
            if pace_data:
                render([player], output_dir, pace_type)
                latest_pace = pace_data[-1]
                image_path = os.path.join(output_dir, player["name"], f'{pace_type}.png')

                embed = discord.Embed(
                    title=f"{player['name']}'s current {pace_type.replace('_', ' ')}",
                    description=f"Your current {pace_type.replace('_', ' ')} is **{latest_pace}**.",
                    color=discord.Color.blue()
                )
                if os.path.exists(image_path):
                    file = discord.File(image_path, filename=f"{pace_type}.png")
                    embed.set_image(url=f"attachment://{pace_type}.png")
                    embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)

                    await ctx.followup.send(file=file, embed=embed)
                else:
                    embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)

                    await ctx.followup.send(embed=embed)
            else:
                await ctx.followup.send(f"No data available for {pace_type}. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
        except Exception as e:
            bot.self.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(PaceCommand(bot))