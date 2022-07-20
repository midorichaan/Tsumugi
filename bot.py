import discord
from discord.ext import commands, tasks

import aiohttp
import os
from dotenv import load_dotenv
from lib import utils
from logging import basicConfig, getLogger, INFO

#load .env
load_dotenv()

#environ JISHAKU
os.environ["NO_UNDERSCORE"] = "True"
os.environ["NO_DM_TRACEBACK"] = "True"

class TsumugiChan(commands.AutoShardedBot):

    def __init__(self, *args, **kwargs) -> None:
        self.logger = kwargs.get("logger", None)
        super().__init__(*args, **kwargs)

        self.instance = {
            "shards": {},
            "ready": False,
            "session": 0,
            "exception": {
                "error": None,
                "traceback": None,
                "context": None
            },
            "channels": {
                "presence": 997358448968740985,
            }
        }

        self._cogs = [
            "cogs.mido_admins", "cogs.mido_events", "cogs.mido_slash", 
            "cogs.mido_presence", "jishaku"
        ]

    #post
    async def post_api(self, status: int=2):
        d = {
            "identity": "tsumugi",
            "status": status
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
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

    #api status poster
    @tasks.loop(minutes=15.0)
    async def api_status_poster(self):
        if self.instance["ready"]:
            await self.post_api(2)
        else:
            await self.post_api(1)

    #overwrite run
    def run(self) -> None:
        token = os.environ.get("TOKEN", None)
        if not token:
            self.logger.critical(
                "RUNNER: Bot token was not provided"
            )
            return
        else:
            try:
                super().run(token)
            except Exception as exc:
                self.logger.critical(f"RUNNER: {exc}")
            else:
                self.logger.info(
                    "RUNNER: Enabling tsumugi discordbot..."
                )

    #setup_hook
    async def setup_hook(self):
        self.logger.info("SYSTEM: Setting up...")

        for i in self._cogs:
            try:
                await self.load_extension(i)
            except Exception as exc:
                self.logger.error(f"ERROR: {exc}")
            else:
                self.logger.info(f"SYSTEM: Cog {i} load")

        try:
            self.api_status_poster.start()
        except Exception as exc:
            self.logger.error(f"ERROR: {exc}")

    #on_ready
    async def on_ready(self) -> None:
        self.logger.info(f"RUNNER: Logged in as {self.user}")
        await self.post_api(1)

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
            self.logger.info("SYSTEM: Presence changed")

        self.instance["ready"] = True
        self.logger.info("RUNNER: Enabled tsumugi discordbot")

#run
if __name__ == "__main__":
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
