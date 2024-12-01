import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render

class WinsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name='wins', description="Show the wins of a player.")
    @app_commands.describe(identifier="The identifier of the player you want to see the wins of.")
    async def wins(self, ctx, identifier: str = None):
        try:
            await ctx.response.defer()
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
                await ctx.response.send_message(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return
            wins_data = player.get("wins")
            if wins_data:
                render([player], output_dir, "wins")
                current_wins = wins_data[-1]
                image_path = os.path.join(output_dir, player["name"], 'wins.png')

                embed = discord.Embed(
                    title=f"{player['name']}'s current wins",
                    description=f"The current wins are **{current_wins}**.",
                    color=discord.Color.brand_red()
                )
                if os.path.exists(image_path):
                    file = discord.File(image_path, filename="wins.png")
                    embed.set_image(url=f"attachment://wins.png")
                    embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)

                    await ctx.followup.send(file=file, embed=embed)
                else:
                    embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)

                    await ctx.followup.send(embed=embed)
            else:
                await ctx.followup.send(f"No data available for wins. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(WinsCommand(bot))