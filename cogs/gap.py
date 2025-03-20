import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta

class GapCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name="gap", description="Show the gap between the player and the player above and below (if any).")
    @app_commands.describe(identifier="The identifier of the player you want to see the gap of.")
    async def gap(self, ctx, identifier: str = None):
        try:
            await ctx.response.defer()
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
                    await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any. Please provide an identifier or link your Discord account (/link)")
                    return
            
            players = find_player(conn, identifier)
            if not players:
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return
            
            if isinstance(players, dict):
                selected_player = players
            elif len(players) == 1:
                selected_player = players[0]
            else:
                class PlayerSelect(discord.ui.Select):
                    def __init__(self, ctx, players):
                        self.ctx = ctx
                        self.players = players
                        options = [
                            discord.SelectOption(label=player['name'], value=str(player['id'])) for player in players
                        ]
                        super().__init__(placeholder="Select a player", options=options)

                    async def callback(self, interaction: discord.Interaction):
                        if interaction.user.id != self.ctx.user.id:
                            await interaction.response.send_message("You cannot select a player for this command.", ephemeral=True)
                            return
                        selected_id = self.values[0]
                        selected_player = next((p for p in self.players if str(p['id']) == selected_id), None)
                        if not selected_player:
                            await interaction.response.send_message("Invalid selection. Please try again.", ephemeral=True)
                            return
                        await interaction.message.delete()
                        await process_gap(self.ctx, selected_player, update, conn)

                class PlayerSelectView(discord.ui.View):
                    def __init__(self, ctx, players):
                        super().__init__()
                        self.add_item(PlayerSelect(ctx, players))
                
                await ctx.followup.send("Multiple players found, please select one:", view=PlayerSelectView(ctx, players))
                return
            
            await process_gap(ctx, selected_player, update, conn)
        
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send("Me no worki lol ask Polo 2 fix plz")

async def process_gap(ctx, player, update, conn):
    pro, noob = find_gap(player, conn)
    embed = discord.Embed(
        title=f"{player['name']} - Points Gap",
        description=f"Points gap comparison for {player['name']}",
        color=0x00b0f4
    )
    pro_gap = abs(pro['points'][-1] - player['points'][-1]) if pro else 1e99
    if pro:
        delta_pro = pro_gap - abs(pro['points'][-2] - player['points'][-2]) if len(player['points']) >= 2 and len(pro['points']) >= 2 else 0
    noob_gap = abs(noob['points'][-1] - player['points'][-1]) if noob else 1e99
    if noob:
        delta_noob = noob_gap - abs(noob['points'][-2] - player['points'][-2]) if len(player['points']) >= 2 and len(noob['points']) >= 2 else 0
    
    if pro:
        estimated_time_pro = int((pro_gap)/(abs(delta_pro) * 4 / 60)) if delta_pro != 0 else 0
        enplus = ""
        if delta_pro > 0:
            enplus = f"*:warning: {pro['name']} is farming faster than you! Skill issue, take this L *"
        else:
            enplus = f"          |--> `around {estimated_time_pro} minutes needed` --> (<t:{int(update.timestamp() + estimated_time_pro * 60)}:R>)"
        embed.add_field(
            name=f" ⬆️ - {pro['ranks'][-1]} - {pro['name']}",
            value=f"• Points : **{pro['points'][-1]:,}**\n•   Gap   :  **{abs(pro['points'][-1] - player['points'][-1]):,}** **({'+' if delta_pro > 0 else ''}{delta_pro:,})**\n{enplus}",
            inline=False
        )
    embed.add_field(
        name=f" ▶️ - {player['ranks'][-1]} - {player['name']}",
        value=f"Points: **{player['points'][-1]:,}**",
        inline=False
    )
    if noob:
        embed.add_field(
            name=f" ⬇️ - {noob['ranks'][-1]} - {noob['name']}",
            value=f"Points: **{noob['points'][-1]:,}**\n"
                  f"Gap: **{abs(player['points'][-1] - noob['points'][-1]):,} ({'+' if delta_noob > 0 else ''}{delta_noob:,})**\n",
            inline=False
        )
    
    embed.add_field(name="Updated at", value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
    await ctx.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GapCommand(bot))
