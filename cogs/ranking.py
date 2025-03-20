import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render
class RankingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name='ranking', description="Show the ranking of a player.")
    @app_commands.describe(identifier="The identifier of the player you want to see the ranking of.")
    async def ranking(self, ctx, identifier: str = None):
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
                    await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                    return

            players = find_player(conn, identifier)

            if not players:
                await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
                return

            if isinstance(players, list):
                if len(players) >= 25:
                    await ctx.followup.send("Too many users found with a matching name. Please be more precise.")
                    return

                select = discord.ui.Select(
                    placeholder="Select the correct player",
                    options=[discord.SelectOption(label=p["name"], value=p["name"]) for p in players]
                )

                async def select_callback(interaction: discord.Interaction):
                    selected_player = next(p for p in players if p["name"] == select.values[0])
                    view.clear_items()
                    await interaction.response.edit_message(view=view)
                    await self.process_player(ctx, selected_player, update)
                    await interaction.message.delete()

                select.callback = select_callback
                view = discord.ui.View()
                view.add_item(select)
                await ctx.followup.send("Multiple players found, please select one:", view=view)
                return

            await self.process_player(ctx, players, update)

        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send("Me no worki lol ask Polo 2 fix plz")

    async def process_player(self, ctx, player, update):
        ranks_data = player.get("ranks")
        if ranks_data:
            render([player], output_dir, "ranks", step=True)
            current_rank = ranks_data[-1]
            image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), 'ranks.png')

            embed = discord.Embed(
                title=f"{player['name']}'s ranking",
                description=f"Your current ranking is **{current_rank:,}**.",
                color=discord.Color.green()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="ranks.png")
                embed.set_image(url=f"attachment://ranks.png")
                embed.add_field(name="Updated at", value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(name="Updated at", value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")

async def setup(bot):
    await bot.add_cog(RankingCommand(bot))
