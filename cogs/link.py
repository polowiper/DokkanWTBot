import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils import *
from datetime import datetime, timedelta
from render import render

class LinkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(name='link', description="Link your Discord account to your Dokkan ig name/ID.")
    @app_commands.describe(identifier="The identifier you want to link your Discord account to.")
    async def link(self, ctx, identifier: str):
        try:
            await ctx.response.defer()
            exist = False
            discord_users = load_discord_users()
            user_id = str(ctx.user.id)

            async def callback_yesconf(interaction: discord.Interaction):
                if int(ctx.user.id) != int(interaction.user.id):
                    return await interaction.followup.send(embed=discord.Embed(
                        description=f"❌ {interaction.user.mention}, - you can't do that !"),
                        ephemeral=True)
                # Remplacer l'identifiant
                discord_users[user_id] = identifier
                save_discord_users(discord_users)
                # Dire que l'identifiant a été remplacé
                await ctx.channel.send(embed=discord.Embed
                (
                    description=f'**✅♻ - Your Discord ID has refreshed and is now linked to player "{identifier}**".',
                    color=discord.Color.blue()
                ))
                await interaction.message.delete()

            async def callback_noconf(interaction: discord.Interaction):
                if int(ctx.user.id) != int(interaction.user.id):
                    return await interaction.followup.send(embed=discord.Embed(
                        description=f"❌ {interaction.user.mention}, - you can't do that !"),
                        ephemeral=True)
                await interaction.message.delete()

            view = discord.ui.View()
            button_validate = discord.ui.Button(style=discord.ButtonStyle.green, emoji="✅", label="Oui")
            button_cancel = discord.ui.Button(style=discord.ButtonStyle.red, emoji="❌", label="Non")
            button_validate.callback = callback_yesconf
            button_cancel.callback = callback_noconf
            view.add_item(button_validate)
            view.add_item(button_cancel)

            # await ctx.send(f'Your Discord ID has been successfully linked to player "{identifier}".'))

            # Check si l'utilisateur existe
            try:
                if type(discord_users[user_id]) is int:
                    pass
                exist = True
            except KeyError: # Existe pas, car erreur
                exist = False

            if exist:
                # Demander si il veut remplacer son identifiant
                await ctx.followup.send(f"Would you like to replace ``{discord_users[str(ctx.user.id)]}`` by ``{identifier}`` ?", view=view, ephemeral=False)
            else:
                # Existe pas
                discord_users[user_id] = identifier
                save_discord_users(discord_users)
                await ctx.send(embed=discord.Embed
                (
                    description=f'**✅ - Your Discord ID has been successfully linked to player "{identifier}**".',
                    color=discord.Color.blue()
                ))
        except Exception as e:
            self.bot.log_message(f"An error occurred: {e}")
            await ctx.followup.send(f"Me no worki lol ask Polo 2 fix plz")

async def setup(bot):
    await bot.add_cog(LinkCommand(bot))