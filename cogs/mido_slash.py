import discord
from discord import app_commands
from discord.ext import commands

class mido_slash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        description="test slash command",
    )
    async def ping(self, interact):
        await interact.response.send_message("はろー！")

async def setup(bot):
    await bot.add_cog(mido_slash(bot))
