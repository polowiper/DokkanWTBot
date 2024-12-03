import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import bulk_render

class BulkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name="bulk", description="Get the bulk infos of a player")
    async def bulk(self, ctx, identifier:str = None):
        try: 
            await ctx.response.defer()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update == None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())
            if identifier is None:
                user_id = str(ctx.user.id)
                identifier = discord_users.get(user_id)
                if identifier is None:
                    await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (!link)")
                    return
            conn = load_db_data()
            player = find_player(conn, identifier)
            if player is None:
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return
            bulk_render([player], output_dir, ["points", "points_pace", "ranks", "wins"])
            image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), 'bulk_points_points_pace_ranks_wins.png')
            embed = discord.Embed(
                title = "Summary ig",
                description = "ab lablalbla",
                color = discord.Color.purple()
                )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="bulk.png")
                embed.set_image(url=f"attachment://bulk.png")
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                await ctx.followup.send(file=file, embed=embed)
            else:
                await ctx.followup.send(embed=embed)
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(BulkCommand(bot))