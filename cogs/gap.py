import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render

class GapCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name = "gap", description="Show the gap between the player and the player above and below (if any).")
    @app_commands.describe(identifier="The identifier of the player you want to see the gap of.")
    async def gap(self, ctx, identifier: str = None):
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
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return
            pro, noob = find_gap(player, conn)
            embed = discord.Embed(
                title=f"{player['name']} - Points Gap",
                description=f"Points gap comparison for {player['name']}",
                color=0x00b0f4
            )
            pro_gap = abs(pro['points'][-1] - player['points'][-1]) if pro else 1e99 #SUPER UGLY FUCKING HELL PLEASE KILL ME 
            if pro:
                delta_pro = pro_gap - abs(pro['points'][-2] - player['points'][-2]) if len(player['points'])>=2 and len(pro['points'])>=2 else 0
            noob_gap = abs(noob['points'][-1] - player['points'][-1]) if noob else 1e99
            if noob:
                delta_noob = noob_gap - abs(noob['points'][-2] - player['points'][-2]) if len(player['points'])>=2 and len(noob['points'])>=2 else 0
            player_arrow = "↗" if pro_gap < noob_gap else "↘"
            if pro:
                pro_arrow = "⬆️"
                """embed.add_field(
                    name=f"{pro_arrow} Nr.{pro['ranks'][-1]}: {pro['name']}",
                    value=f"Points: **{pro['points'][-1]:,}**\n"
                        f"Gap: **{abs(pro['points'][-1] - player['points'][-1]):,} ({'+' if delta_pro > 0 else ''}{delta_pro:,})**",
                    inline=False
                )"""
                estimated_time_pro = round((pro_gap / ( delta_pro * 4))*60) if delta_pro != 0 else 0
                enplus = ""
                if pro['points_pace'][-1] > player['points_pace'][-1] : # l'user est plus lent que le prochain
                    enplus = f"*:warning: {pro['name']} is farming faster than you ! Skill issue, take this L *"
                else: # on est plus rapide !
                    enplus = f"          |--> `around {estimated_time_pro} minutes needed` --> ( <t:{int(update.timestamp() + estimated_time_pro*60)}:R> TO BE FIXED XD)"
                embed.add_field(name=f" ⬆️ - {pro['ranks'][-1]} - {pro['name']}",
                                value=f"• Points : **{pro['points'][-1]:,}**\n•   Gap   :  **{abs(pro['points'][-1] - player['points'][-1]):,}** **({'+' if delta_pro > 0 else ''}{delta_pro:,})**\n{enplus}",
                                inline=False)
            embed.add_field(
                name=f" ▶️ - {player['ranks'][-1]} - {player['name']}",
                value=f"Points: **{player['points'][-1]:,}**",
                inline=False
            )
            if noob:
                noob_arrow = "⬇️"
                embed.add_field(
                    name=f" ⬇️ - {noob['ranks'][-1]} - {noob['name']}",
                    value=f"Points: **{noob['points'][-1]:,}**\n"
                        f"Gap: **{abs(player['points'][-1] - noob['points'][-1]):,} ({'+' if delta_noob > 0 else ''}{delta_noob:,})**\n",
                    inline=False
                )

            embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)

            await ctx.followup.send(embed=embed)
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(GapCommand(bot))
