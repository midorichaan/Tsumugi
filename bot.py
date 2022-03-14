import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
from logging import basicConfig, getLogger, INFO

#load .env
load_dotenv()

class TsumugiChan(commands.AutoShardedBot):

    def __init__(self, *args, **kwargs) -> None:
        self.logger = kwargs.get("logger", None)
        super().__init__(*args, **kwargs)

        self.instance = {
            "shards": {},
            "session": 0
        }

        self._cogs = [
            "cogs.mido_admins", "jishaku"
        ]

    #overwrite run
    def run(self) -> None:
        token = os.environ.get("TOKEN", None)
        if not token:
            self.logger.critical(
                "bot token was not provided"
            )
            return
        else:
            try:
                super().run(token)
            except Exception as exc:
                self.logger.critical(exc)
            else:
                self.logger.info(
                    "Enabling tsumugi discordbot..."
                )

    #on_connect
    async def on_connect(self) -> None:
        self.logger.info(
            "Successfully connected to Discord"
        )

        for i in range(self.shard_count):
            self.instance["shards"][i] = 0
        self.instance["session"] = 1

    #on_disconnect
    async def on_disconnect(self) -> None:
        self.logger.warning(
            "Successfully connected to Discord"
        )
        self.instance["session"] = 0

    #on_shard_connect
    async def on_shard_connect(self, shard_id: int) -> None:
        self.logger.info(
            f"Shard ID {shard_id} has successfully connected to Discord"
        )
        self.instance["shards"][shard_id] = 1

    #on_shard_disconnect
    async def on_shard_disconnect(self, shard_id: int) -> None:
        self.logger.warning(
            f"Shard ID {shard_id} has disconnected from Discord"
        )
        self.instance["shards"][shard_id] = 0

    #on_shard_ready
    async def on_shard_ready(self, shard_id: int) -> None:
        self.logger.info(
            f"Shard ID {shard_id} has become ready"
        )
        self.instance["shards"][shard_id] = 2

    #on_shard_resumed
    async def on_shard_resumed(self, shard_id: int) -> None:
        self.logger.info(
            f"Shard ID {shard_id} has resumed"
        )
        self.instance["shards"][shard_id] = 2

    #on_resumed
    async def on_resumed(self):
        self.logger.info(
            "Session has resumed"
        )
        self.instance["session"] = 1

    #on_ready
    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user}")

        for i in self._cogs:
            try:
                await self.load_extension(i)
            except Exception as exc:
                self.logger.error(exc)
            else:
                self.logger.info(f"Cog {i} load")

        try:
            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Game(
                    "のんびりお茶ちう...><"
                )
            )
        except Exception as exc:
            self.logger.error(exc)
        else:
            self.logger.info("Presence changed")

        self.logger.info("Enabled tsumugi discordbot")

#logger
basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s]: %(message)s"
)
logger = getLogger("discord")

#vars
intents = discord.Intents.all()

#instance
bot = TsumugiChan(
    logger=logger,
    intents=intents,
    command_prefix=os.environ.get("PREFIX", "."),
    shard_count=2,
    status=discord.Status.idle
)
bot.run()
