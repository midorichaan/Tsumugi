import discord
from discord.ext import commands

class mido_events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

                self.instance["shards"][i] = 0
        self.instance["session"] = 1

    #on_shard_connect
    async def on_shard_connect(self, shard_id: int) -> None:
        self.bot.logger.info(
            f"SESSION: Shard ID {shard_id} has successfully connected to Discord"
        )
        self.bot.instance["shards"][shard_id] = 1

    #on_shard_disconnect
    async def on_shard_disconnect(self, shard_id: int) -> None:
        self.bot.logger.warning(
            f"Shard ID {shard_id} has disconnected from Discord"
        )
        self.bot.instance["shards"][shard_id] = 0

    #on_shard_ready
    async def on_shard_ready(self, shard_id: int) -> None:
        self.bot.logger.info(
            f"SESSION: Shard ID {shard_id} has become ready"
        )
        self.bot.instance["shards"][shard_id] = 2

    #on_shard_resumed
    async def on_shard_resumed(self, shard_id: int) -> None:
        self.bot.logger.info(
            f"SESSION: Shard ID {shard_id} has resumed"
        )
        self.bot.instance["shards"][shard_id] = 2

    #on_resumed
    async def on_resumed(self) -> None:
        self.bot.logger.info(
            "SESSION: Session has resumed"
        )
        self.bot.instance["session"] = 1

    #on_disconnect
    async def on_disconnect(self) -> None:
        self.bot.logger.warning(
            "SESSION: Successfully disconnected to Discord"
        )
        self.bot.instance["session"] = 0

#setup
async def setup(bot):
    await bot.add_cog(mido_events(bot))
