import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render

class RandomSeedCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name='rseed', description="Show the seed performance of a player relative to a certain amount of resets.")
    @app_commands.describe(identifier="The identifier of the player you want to see the seed performance of.", resets_amount="The amount of resets you want to use to calculate your seed.")
    async def rseed(self, ctx, identifier: str = None, resets_amount: int = None):
        try:
            await ctx.response.defer()
            if resets_amount is None:
                await ctx.followup.send("You didn't provide a resets amount, please provide one.")
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

           
            current_hour = round(elapsed.days * 24 + elapsed.seconds / 3600, 2)
            self.bot.log_message(f"Current hour is {current_hour}")
            conn.create_function("strrev", 1, lambda s: s[::-1])
            
            query_player = f"""
            WITH RankedPlayers AS (
                SELECT 
                    id,
                    name,

                    CAST(SUBSTR(points, LENGTH(points) - INSTR(strrev(points), ',') + 2) AS FLOAT) AS latest_points,
                    CAST(SUBSTR(points, LENGTH(points) - 
                        INSTR(strrev(SUBSTR(points, 1, LENGTH(points) - INSTR(strrev(points), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT) AS previous_points,

                    CAST(SUBSTR(wins, LENGTH(wins) - INSTR(strrev(wins), ',') + 2) AS FLOAT) AS latest_wins,
                    CAST(SUBSTR(wins, LENGTH(wins) - 
                        INSTR(strrev(SUBSTR(wins, 1, LENGTH(wins) - INSTR(strrev(wins), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT) AS previous_wins,

                    (CAST(SUBSTR(points, LENGTH(points) - INSTR(strrev(points), ',') + 2) AS FLOAT) - 
                     CAST(SUBSTR(points, LENGTH(points) - 
                         INSTR(strrev(SUBSTR(points, 1, LENGTH(points) - INSTR(strrev(points), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) /
                    (CAST(SUBSTR(wins, LENGTH(wins) - INSTR(strrev(wins), ',') + 2) AS FLOAT) - 
                     CAST(SUBSTR(wins, LENGTH(wins) - 
                         INSTR(strrev(SUBSTR(wins, 1, LENGTH(wins) - INSTR(strrev(wins), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) AS relative_seed,

                    ROW_NUMBER() OVER (ORDER BY 
                        (CAST(SUBSTR(points, LENGTH(points) - INSTR(strrev(points), ',') + 2) AS FLOAT) - 
                         CAST(SUBSTR(points, LENGTH(points) - 
                             INSTR(strrev(SUBSTR(points, 1, LENGTH(points) - INSTR(strrev(points), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) /
                        (CAST(SUBSTR(wins, LENGTH(wins) - INSTR(strrev(wins), ',') + 2) AS FLOAT) - 
                         CAST(SUBSTR(wins, LENGTH(wins) - 
                             INSTR(strrev(SUBSTR(wins, 1, LENGTH(wins) - INSTR(strrev(wins), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) DESC
                    ) AS position
                FROM players
                WHERE 
                    LENGTH(hour) - LENGTH(REPLACE(hour, ',', '')) + 1 >= {resets_amount} AND
                    CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2) AS FLOAT) = ?
            )
            SELECT
                name,
                relative_seed,
                position,
                latest_points,
                previous_points,
                latest_wins,
                previous_wins
            FROM RankedPlayers
            WHERE id = ? or name = ?;
            """
            query = f"""
            WITH RankedPlayers AS (
                SELECT 
                    id,
                    name,

                    CAST(SUBSTR(points, LENGTH(points) - INSTR(strrev(points), ',') + 2) AS FLOAT) AS latest_points,
                    CAST(SUBSTR(points, LENGTH(points) - 
                        INSTR(strrev(SUBSTR(points, 1, LENGTH(points) - INSTR(strrev(points), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT) AS previous_points,

                    CAST(SUBSTR(wins, LENGTH(wins) - INSTR(strrev(wins), ',') + 2) AS FLOAT) AS latest_wins,
                    CAST(SUBSTR(wins, LENGTH(wins) - 
                        INSTR(strrev(SUBSTR(wins, 1, LENGTH(wins) - INSTR(strrev(wins), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT) AS previous_wins,

                    (CAST(SUBSTR(points, LENGTH(points) - INSTR(strrev(points), ',') + 2) AS FLOAT) - 
                     CAST(SUBSTR(points, LENGTH(points) - 
                         INSTR(strrev(SUBSTR(points, 1, LENGTH(points) - INSTR(strrev(points), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) /
                    (CAST(SUBSTR(wins, LENGTH(wins) - INSTR(strrev(wins), ',') + 2) AS FLOAT) - 
                     CAST(SUBSTR(wins, LENGTH(wins) - 
                         INSTR(strrev(SUBSTR(wins, 1, LENGTH(wins) - INSTR(strrev(wins), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) AS relative_seed,

                    ROW_NUMBER() OVER (ORDER BY 
                        (CAST(SUBSTR(points, LENGTH(points) - INSTR(strrev(points), ',') + 2) AS FLOAT) - 
                         CAST(SUBSTR(points, LENGTH(points) - 
                             INSTR(strrev(SUBSTR(points, 1, LENGTH(points) - INSTR(strrev(points), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) /
                        (CAST(SUBSTR(wins, LENGTH(wins) - INSTR(strrev(wins), ',') + 2) AS FLOAT) - 
                         CAST(SUBSTR(wins, LENGTH(wins) - 
                             INSTR(strrev(SUBSTR(wins, 1, LENGTH(wins) - INSTR(strrev(wins), ',') * ({resets_amount} - 1))), ',') + 2) AS FLOAT)) DESC
                    ) AS position
                FROM players
                WHERE 
                    LENGTH(hour) - LENGTH(REPLACE(hour, ',', '')) + 1 >= {resets_amount} AND
                    CAST(SUBSTR(hour, LENGTH(hour) - INSTR(strrev(hour), ',') + 2) AS FLOAT) = ?
            )
            SELECT
                name,
                relative_seed,
                position
            FROM RankedPlayers
            LIMIT 10;
            """
            cursor = conn.cursor()
            cursor.execute(query, (current_hour,))
            seed_lb = cursor.fetchall()
            
            if seed_lb is None:
                await ctx.followup.send(f"There's a problem with the database chief, We might be fucking cooked, ask polo 2 fix plz")
                return
            self.bot.log_message(f"Found {len(seed_lb)} players with relative seed")
            cursor.execute(query_player, (current_hour, identifier, identifier))
            player = cursor.fetchone()
            if player is None:
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return
            self.bot.log_message(f"Found player with name or ID {identifier}")
            

            #Just a portion of debugging to see if the query gives the right result
            test_player = find_player(conn, identifier)
            test_relative_seed = (test_player["points"][-resets_amount] - test_player["points"][-1]) / (test_player["wins"][-resets_amount] - test_player["wins"][-1])
            latest_points = player[3]
            previous_points = player[4]
            latest_wins = player[5]
            previous_wins = player[6]

            test_latest_points = test_player["points"][-1]
            test_previous_points = test_player["points"][-resets_amount]
            test_latest_wins = test_player["wins"][-1]
            test_previous_wins = test_player["wins"][-resets_amount]

            player_name = player[0]
            player_relative_seed = player[1]
            player_rank = player[2]
            self.bot.log_message(f"""
            {player_name} Debug:

            Latest points db: {latest_points}             |      Latest_points real: {test_latest_points}    
            Previous points db: {previous_points}         |      Previous_points real: {test_previous_points}
            Latest wins db: {latest_wins}                 |      Latest_wins real: {test_latest_wins}
            Previous wins db: {previous_wins}             |      Previous_wins real: {test_previous_wins}

            Relative seed db: {player_relative_seed}      |      Relative seed real: {test_relative_seed}
            
            """)

#            self.bot.log_message(f"Found player with name {player_name} and relative seed {player_relative_seed}, rank {player_rank}")
            embed = discord.Embed(
                title="🏆 Top seed Leaderboard 🏆",
                description=f"Here are the top 10 players with the highest relative seed over the last {resets_amount} resets.",
                color=discord.Color.gold()
            )

            for idx, player in enumerate(seed_lb, start=1): #Yeah now that I think about it it's pretty retarded to make all of that command in order to get the position of a player with its relative_seed only to fucking dump it later on
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
                        value=f"Relative Seed: **{player[1]:.2f}**",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"{rank_emoji} {player[0]}",
                        value=f"Relative Seed: **{player[1]:.2f}**",
                        inline=False
                    )

            if player_name not in [player[0] for player in seed_lb]:
                embed.add_field(
                    name="🔍 Player Not in Top 10",
                    value=(
                        f"**{player_name}** is ranked **#{player_rank}** "
                        f"with a Relative Seed of **{player_relative_seed:.2f}**."
                    ),
                    inline=False
                )

            embed.set_footer(
                text=f"Displaying leaderboard for relative seed (hope you're in the top 10 pookie). "
            )
            embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)


            await ctx.followup.send(embed=embed)
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(RandomSeedCommand(bot))