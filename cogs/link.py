from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import load_discord_users, save_discord_users


class LinkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        globals()["bot"] = bot

    @app_commands.command(
        name="link", description="Link your Discord account to your Dokkan ig name/ID."
    )
    @app_commands.describe(
        identifier="The identifier you want to link your Discord account to."
    )
    async def link(self, interaction: discord.Interaction, identifier: str):
        await interaction.response.defer(ephemeral=True)
        discord_users = load_discord_users()
        user_id = str(interaction.user.id)

        async def callback_yesconf(interaction: discord.Interaction):
            if int(user_id) != int(interaction.user.id):
                return await interaction.followup.send(
                    embed=discord.Embed(
                        description=f"❌ {interaction.user.mention}, you can't do that!"
                    ),
                    ephemeral=True,
                )
            discord_users[user_id] = identifier
            save_discord_users(discord_users)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f'**✅♻ - Your Discord ID has refreshed and is now linked to player "{identifier}**".',
                    color=discord.Color.blue(),
                ),
                ephemeral=False,
            )

        async def callback_noconf(interaction: discord.Interaction):
            if int(user_id) != int(interaction.user.id):
                return await interaction.followup.send(
                    embed=discord.Embed(
                        description=f"❌ {interaction.user.mention}, you can't do that!"
                    ),
                    ephemeral=True,
                )
            await interaction.response.send_message(
                embed=discord.Embed(description="❌ Linking cancelled."), ephemeral=True
            )

        view = discord.ui.View()
        button_validate = discord.ui.Button(
            style=discord.ButtonStyle.green, emoji="✅", label="Yes"
        )
        button_cancel = discord.ui.Button(
            style=discord.ButtonStyle.red, emoji="❌", label="No"
        )
        button_validate.callback = callback_yesconf
        button_cancel.callback = callback_noconf
        view.add_item(button_validate)
        view.add_item(button_cancel)

        if user_id in discord_users:
            await interaction.followup.send(
                f"Would you like to replace ``{discord_users[user_id]}`` with ``{identifier}``?",
                view=view,
                ephemeral=False,
            )
        else:
            discord_users[user_id] = identifier
            save_discord_users(discord_users)
            await interaction.followup.send(
                embed=discord.Embed(
                    description=f'**✅ - Your Discord ID has been successfully linked to player "{identifier}**".',
                    color=discord.Color.blue(),
                ),
                ephemeral=False,
            )


async def setup(bot):
    await bot.add_cog(LinkCommand(bot))

