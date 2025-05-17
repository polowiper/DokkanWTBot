import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render
import typing


class LeaderboardCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    # Autocompletion leaderboard
    async def autocompletion_type_lb(
            self, interaction: discord.Interaction,
            current: str) -> typing.List[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name=a, value=a) for a in [
                "wins_pace", "points_pace", "wins", "points", "points_wins",
                'ranks'
            ]
        ]
        return choices

    @app_commands.command(name="leaderboard",
                          description="Show the top players leaderboard.")
    @app_commands.autocomplete(type=autocompletion_type_lb)
    @app_commands.describe(
        type=
        "The type of leaderboard you want to see. Either 'wins', 'points', 'ranks', 'wins_pace' or 'points_pace'.",
        page="The page of the leaderboard you want to see.")
    async def leaderboard(self, ctx, type: str = "points", page: int = 1):
        try:
            await ctx.response.defer()
            # vérifier si le type est valide
            if type not in [
                    "wins_pace", "points_pace", "wins", "points", "points_wins"
            ]:
                await ctx.followup.send(
                    "Please provide a valid type. Either 'wins_pace', 'points_wins', 'points_pace', 'wins' or 'points'."
                )
                return
            players_per_page = 10
            offset = (page - 1) * players_per_page
            conn = load_db_data()
            update, start, end, total, left, elapsed = time_data()
            if update is None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())
            datatypes = {
                "wins_pace": "FLOAT",
                "points_pace": "FLOAT",
                "wins": "INTEGER",
                "points": "INTEGER",
                "points_wins": "FLOAT",
                "ranks": "INTEGER"
            }
            current_hour = 71.26 if elapsed is None else round(
                elapsed.days * 24 + elapsed.seconds / 3600, 2
            )  #71.26 is the standart wt duration time (i'm saying that because sometimes it's not 71.26 hours ex: The 55th edition that got extended)
            conn.create_function("strrev", 1, lambda s: s[::-1])
            query = f"""
                SELECT name,
                       CAST(SUBSTR({type}, LENGTH({type}) - INSTR(strrev({type}), ',') + 2, LENGTH({type})) AS {datatypes[type]}) AS latest_type_value
                FROM players
                WHERE CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2, LENGTH(hour)) AS FLOAT) = ?
                ORDER BY latest_type_value DESC
                LIMIT ? OFFSET ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (current_hour, players_per_page, offset))
            lb = cursor.fetchall()

            if not lb:
                embed = discord.Embed(
                    title="🏆 Top Players Leaderboard 🏆",
                    description=
                    "No players found for the current leaderboard criteria.",
                    color=discord.Color.red())
                await ctx.followup.send(embed=embed)
                return

            cursor.execute(
                f"""
                SELECT COUNT(*) FROM players
                WHERE CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2, LENGTH(hour)) AS FLOAT) = ?
            """, (current_hour, ))
            total_players = cursor.fetchone()[0]
            total_pages = (total_players + players_per_page -
                           1) // players_per_page

            embed = discord.Embed(
                title="🏆 Top Players Leaderboard 🏆",
                description=
                f"Here are the players ranked {offset + 1} to {min(offset + players_per_page, total_players)} with the highest {type}.",
                color=discord.Color.gold())

            for idx, (name, comp) in enumerate(lb, start=offset + 1):
                if idx == 1:
                    rank_emoji = "🥇"
                elif idx == 2:
                    rank_emoji = "🥈"
                elif idx == 3:
                    rank_emoji = "🥉"
                else:
                    rank_emoji = f"**#{idx}**"

                embed.add_field(name=f"{rank_emoji} {name}",
                                value=f"{type.capitalize()}: **{comp:,}**",
                                inline=False)
            embed.add_field(
                name="Updated at",
                value=
                f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)",
                inline=False)
            embed.set_footer(text=f"Page {page} of {total_pages}")
            await ctx.followup.send(embed=embed)
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo (@polowiper) 2 fix plz")


async def setup(bot):
    await bot.add_cog(LeaderboardCommand(bot))
