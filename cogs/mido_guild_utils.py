import discord
from discord import app_commands
from discord.ext import commands

class mido_guild_utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild_settings_info = [
            "name", "description", "icon", "banner", "splash", "discovery_splash",
            "community", "afk_channel", "afk_timeout", "owner", "verification_level",
            "default_notifications", "explicit_content_filter", "vanity_code",
            "system_channel", "system_channel_flags", "preferred_locale", "rules_channel",
            "public_updates_channel", "premium_progress_bar_enabled", "discoverable",
            "invites_disabled"
        ]

    #settings
    @app_commands.command(
        name="settings",
        description="サーバーの設定を変更します"
    )
    async def _settings(self, interact: discord.Interaction, settings_var: str, value, reason: str=None):
        pass

async def setup(bot):
    await bot.add_cog(mido_guild_utils(bot))
