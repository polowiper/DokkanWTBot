import discord
from discord import app_commands
from discord.ext import commands
from render import render
import os
from cogs.utils import *
from datetime import date
class CompareCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot


    async def autocompletion_type_cmp(self, interaction: discord.Interaction, current: str):
        choices = [
            app_commands.Choice(name=a, value=b)
            for (a, b) in [
                ("points pace", "points_pace"), 
                ("wins pace", "wins_pace"), 
                ("ranking", "ranks"), 
                ("wins", "wins"), 
                ("points", "points"), 
                ("seed", "points_wins"), 
                ("max wins", "max_wins"), 
                ("max points", "max_points")
            ]
        ]
        return choices

    @app_commands.command(name="compare", description="Compare multiple users.")
    @app_commands.describe(
        type="The type of comparison you want to see. Either 'wins', 'points', or 'ranks'.",
        users="The users you want to compare (ex. /compare type:points users:User1 User2)."
    )
    @app_commands.autocomplete(type=autocompletion_type_cmp)
    async def compare(self, ctx, type: str = None, users: str = None):
        try:
            await ctx.response.defer()
            if type not in ["points_pace", "wins_pace", "ranks", "wins", "points", "points_wins", "max_wins", "max_points"]:
                await ctx.followup.send("Please provide a valid type. Either 'wins', 'points', 'max_points', 'max_wins', 'wins_pace', 'points_pace' or 'ranks'.")
                return

            user_list = users.split(" ")
            if len(user_list) < 2:
                await ctx.followup.send("Please provide at least 2 users to compare.")
                return

            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()
            if update == None:
                update = date.fromisoformat('2005-03-30')
                update = datetime.combine(update, datetime.min.time())
            player_list = []
            not_found = []
            conn = load_db_data()
            for user in user_list:
                player = find_player(conn, user)
                if player is None:
                    not_found.append(user)
                    continue
                player_list.append(player)

            if not_found:
                await ctx.followup.send(f"Players not found: {', '.join(not_found)}.")
                return

            render(player_list, "top100_data", type, multiple=True)
            image_path = os.path.join("top100_data", f"multiple{type}.png")

            embed = discord.Embed(
                title="Comparison",
                description=f"Here's the {type} comparison between {', '.join(user_list[:-1])}, and {user_list[-1]}.",
                color=discord.Color.blurple()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="comparison.png")
                embed.set_image(url="attachment://comparison.png")
                embed.add_field(
                    name="Updated at",
                    value=f"<t:{int(update.timestamp())}:f> (<t:{int(update.timestamp())}:R>)",
                    inline=False
                )
                await ctx.followup.send(file=file, embed=embed)
            else:
                await ctx.followup.send("No comparison image was generated.")
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(CompareCommand(bot))
