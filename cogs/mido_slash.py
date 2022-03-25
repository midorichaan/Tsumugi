from discord import app_commands
from discord.ext import commands

class mido_slash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        guild=discord.Object(701131006698192916),
        description="test slash command"
    )
    async def ping(self, interact):
        await interact.response.send_message("はろー！")

async def setup(bot):
    await bot.add_cog(mido_slash(bot))
    await bot.tree.sync(guild=discord.Object(701131006698192916))