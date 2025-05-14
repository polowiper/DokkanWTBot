import json
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import *


class RandomSeedCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(
        name="rseed",
        description="Show the seed performance of a player relative to a certain amount of resets.",
    )
    @app_commands.describe(
        identifier="Player identifier (name/ID).",
        resets_amount="Number of resets for calculation.",
    )
    async def rseed(self, ctx, identifier: str = None, resets_amount: int = None):
        try:
            await ctx.response.defer()

            if resets_amount is None:
                await ctx.followup.send(
                    "You didn't provide a resets amount, please provide one."
                )
                return

            conn = load_db_data()
            discord_users = load_discord_users()
            update, start, end, total, left, elapsed = time_data()

            if update is None:
                update = datetime.fromisoformat("2005-03-30")
                update = datetime.combine(update, datetime.min.time())

            if identifier is None:
                user_id = str(ctx.user.id)
                identifier = discord_users.get(user_id)
                if identifier is None:
                    await ctx.followup.send(
                        "You did not provide a Dokkan name/ID and your Discord account isn't linked. Please provide an identifier or link your Discord account (/link)."
                    )
                    return

            current_hour = (
                round(elapsed.days * 24 + elapsed.seconds / 3600, 2)
                if elapsed
                else 71.26
            )
            print(f"Current hour is {current_hour}")
            conn.create_function("strrev", 1, lambda s: s[::-1])

            cursor = conn.cursor()
            query = "SELECT name, points, wins, id FROM players WHERE CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2) AS FLOAT) = ?"
            cursor.execute(query, (current_hour,))
            seed_lb = cursor.fetchall()

            if not seed_lb:
                await ctx.followup.send(
                    "There's a problem with the database chief, We might be cooked. Ask Polo to fix it."
                )
                return

            player_list = []
            for player in seed_lb:
                name = player[0]
                player_points = json.loads(player[1])
                player_wins = json.loads(player[2])
                if len(player_wins) < resets_amount:
                    continue
                player_id = player[3]  # Fixed incorrect index

                if (
                    len(player_points) < resets_amount
                    or len(player_wins) < resets_amount
                ):
                    wins_diff = player_wins[-1] - player_wins[0]
                    player_relative_seed = (
                        int((player_points[-1] - player_points[0]) / wins_diff)
                        if wins_diff != 0
                        else 0
                    )
                else:
                    wins_diff = player_wins[-1] - player_wins[-resets_amount]
                    player_relative_seed = (
                        int(
                            (player_points[-1] - player_points[-resets_amount])
                            / wins_diff
                        )
                        if wins_diff != 0
                        else 0
                    )
                player_list.append((name, player_relative_seed, player_id))

            player_list.sort(key=lambda x: x[1], reverse=True)

            index = None
            player_name = ""
            for i, player in enumerate(player_list):
                if player[0] == identifier or player[2] == identifier:
                    index = i
                    player_name = player[0]
                    break

            # print(player_name, index)
            embed = discord.Embed(
                title="🏆 Top Seed Leaderboard 🏆",
                description=f"Here are the top 10 players with the highest relative seed over the last {resets_amount} resets.",
                color=discord.Color.gold(),
            )

            top_10_list = player_list[:10]
            for idx, player in enumerate(top_10_list, start=1):
                if idx == 1:
                    rank_emoji = "🥇"
                elif idx == 2:
                    rank_emoji = "🥈"
                elif idx == 3:
                    rank_emoji = "🥉"
                else:
                    rank_emoji = f"**#{idx}**"
                if player[0] == player_name:
                    embed.add_field(
                        name=f"🔍 {rank_emoji} {player[0]} (You!)",
                        value=f"Relative Seed: **{player[1]}**",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"{rank_emoji} {player[0]}",
                        value=f"Relative Seed: **{player[1]}**",
                        inline=False,
                    )

            if index is not None and player_name not in [p[0] for p in top_10_list]:
                player = player_list[index]
                embed.add_field(
                    name="🔍 Player Not in Top 10",
                    value=f"**{player[0]}** is ranked **#{index+1}** with a Relative Seed of **{player[1]}**.",
                    inline=False,
                )

            embed.set_footer(
                text=f"Displaying leaderboard for relative seed. Hope you're in the top 10!"
            )
            embed.add_field(
                name="Updated at",
                value=f"<t:{int(update.timestamp())}:f> (<t:{int(update.timestamp())}:R>)",
                inline=False,
            )

            await ctx.followup.send(embed=embed)
        except Exception as e:
            print(f"An error occurred: {e}")
            await ctx.followup.send("Me no worki lol. Ask Polo to fix plz.")


async def setup(bot):
    await bot.add_cog(RandomSeedCommand(bot))
