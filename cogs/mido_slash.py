import discord
from discord import app_commands
from discord.ext import commands

import time

guild_id = discord.Object(id=701131006698192916)

class mido_slash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #ping command
    @app_commands.command(
        name="ping",
        description="BotのPingを返します"
    )
    async def _ping(self, interact: discord.Interaction):
        msg = await interact.response.send_message(
            "> Pinging...",
            ephemeral=True
        )

        msg_time = time.perf_counter()
        ws = round(self.bot.latency * 1000, 2)
        ping = round(time.perf_counter() - msg_time, 3) * 1000

        await interact.edit_original_message(
            content=f"> 🏓Pong! \nPing: {ping}ms \nWebSocket: {ws}ms"
        )

async def setup(bot):
    await bot.add_cog(mido_slash(bot))
