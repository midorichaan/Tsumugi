import discord
from discord.ext import commands, tasks

import aiohttp
import os
import traceback
from dotenv import load_dotenv
from lib import utils
from logging import basicConfig, getLogger, INFO

#load .env
load_dotenv()

class TsumugiChan(commands.AutoShardedBot):

    def __init__(self, *args, **kwargs) -> None:
        self.logger = kwargs.get("logger", None)
        super().__init__(*args, **kwargs)

        self.session = aiohttp.ClientSession()
        self.instance = {
            "shards": {},
            "session": 0,
            "exception": {
                "error": None,
                "traceback": None,
                "context": None
            }
        }

        self._cogs = [
            "cogs.mido_admins", "jishaku"
        ]

    #api status poster
    @tasks.loop(minutes=15.0)
    async def api_status_poster(self):
        d = {
            "identity": "tsumugi",
        }

        if not self.vars["maintenance"]:
            d["status"] = 2

            try:
                async with self.session.request(
                    "POST",
                    "https://api.midorichan.cf/v1/service/status",
                    headers={"Authorization": f"Bearer {os.environ['MIDORI_API']}"},
                    json=d
                ) as request:
                    data = await discord.http.json_or_text(request)
                    if request.status == 200:
                        self.logger.info(f"API: Updated service status - {data}")
                    else:
                        self.logger.warning(f"API: Service status update failed - {data}")
            except Exception as exc:
                self.logger.warning(f"ERROR: {exc}")
        else:
            d["status"] = 1

            try:
                async with self.session.request(
                    "POST",
                    "https://api.midorichan.cf/v1/service/status",
                    headers={"Authorization": f"Bearer {os.environ['MIDORI_TOKEN']}"},
                    json=d
                ) as request:
                    data = await discord.http.json_or_text(request)
                    if request.status == 200:
                        self.logger.info(f"API: Updated service status - {data}")
                    else:
                        self.logger.warning(f"API: Service status update failed - {data}")
            except Exception as exc:
                self.logger.warning(f"ERROR: {exc}")

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
    async def on_resumed(self) -> None:
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
            api_status_poster.start()
        except Exception as exc:
            self.logger.error(exc)

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

    #on_command
    async def on_command(self, ctx) -> None:
        if isinstance(ctx.channel, discord.DMChannel):
            format = f"COMMAND: {ctx.author} ({ctx.author.id}) -> {ctx.message.content} @DM"
            self.logger.info(format)
        else:
            format = f"COMMAND: {ctx.author} ({ctx.author.id}) -> {ctx.message.content} @{ctx.channel} ({ctx.channel.id}) - {ctx.guild} ({ctx.guild.id})"
            self.logger.info(format)

    #on_command_error
    async def on_command_error(self, ctx, exc) -> None:
        traceback_exc = ''.join(
            traceback.TracebackException.from_exception(exc).format()
        )
        format = ""

        self.instance["exception"] = {
            "error": exc,
            "traceback": traceback_exc,
            "context": ctx
        }

        if isinstance(ctx.channel, discord.DMChannel):
            format = f"ERROR: {ctx.author} ({ctx.author.id}) -> {exc} @DM"
        else:
            format = f"ERROR: {ctx.author} ({ctx.author.id}) -> {exc} @{ctx.channel} ({ctx.channel.id}) - {ctx.guild} ({ctx.guild.id})"

        self.logger.warning(format)
        await utils.reply_or_send(
            ctx,
            content=f"> エラー \n```py\n{exc}\n```"
        )

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
