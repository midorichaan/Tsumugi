import discord
from discord import app_commands
from discord.ext import commands

import io
import os
import textwrap
import traceback
from contextlib import redirect_stdout
from twitter import Twitter, OAuth
from lib import utils

#is_owner
def is_owner():
    async def p(i: discord.Interaction):
        if not await i.client.is_owner(i.user):
            return await i.response.send_message(
                content=f"> このコマンドは使用できません"
            )
        return True
    return app_commands.check(p)

class mido_slash_admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._ = None

    #tweet
    @app_commands.command(name="tweet", description="ツイートします")
    @app_commands.describe(text="ツイートする内容")
    @is_owner()
    async def _tweet(self, interact: discord.Interaction, *, text: str=None):
        if not text:
            return await interact.response.send_message(
                content=f"> ツイートする内容を入力してください"
            )

        try:
            d = self.bot.twitter.statuses.update(status=text)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )
        else:
            return await interact.response.send_message(
                content=f"> https://twitter.com/{d['user']['screen_name']}/status/{d['id']}",
                ephemeral=True
            )

    #shell
    @app_commands.command(name="shell", description="シェルコマンドを実行します")
    @app_commands.describe(command="実行するコマンド")
    @is_owner()
    async def _shell(self, interact: discord.Interaction, *, command: str=None):
        if not command:
            return await interact.response.send_message(
                content=f"> コマンドを入力してください"
            )

        try:
            stdout, stderr = await utils.run_process(interact, command)
            if stderr:
                text = f"```\nstdout: \n{stdout} \n\nstderr: \n{stderr}\n```"
            else:
                text = f"```\nstdout: \n{stdout} \n\nstderr: \nNone\n```"
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )
        else:
            return await interact.response.send_message(
                content=text
            )

    #eval
    @app_commands.command(name="eval", description="Pythonのコードを評価します")
    @app_commands.describe(code="評価するコード")
    @is_owner()
    async def _eval(self, interact: discord.Interaction, *, code: str=None):
        if not code:
            return await interact.response.send_message(
                content=f"> 評価するコードを入力してください"
            )

        env = {
            'bot': self.bot,
            'interact': interact,
            'self': self,
            '_': self._
        }

        env.update(globals())
        code = utils.cleanup_code(code)
        stdout = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"```py\n{exc.__class__.__name__}: {exc}\n```"
            )

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as exc:
            value = stdout.getvalue()
            return await interact.response.send_message(
                content=f'```py\n{value}{traceback.format_exc()}\n```'
            )
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await interact.response.send_message(
                        content=f'```py\n{value}\n```'
                    )
                else:
                    await interact.response.send_message(
                        content=f"```py\nNone\n```"
                    )
            else:
                self._ = ret
                await interact.response.send_message(
                    content=f'```py\n{value}{ret}\n```'
                )

    #group instance
    group = app_commands.Group(
        name="admin",
        description="管理者用コマンド"
    )

    #admin reload
    @group.command(name="reload", description="ファイルの再読み込みを行います")
    @app_commands.describe(module="再読み込みするCog")
    @is_owner()
    async def _reload(self, interact: discord.Interaction, module: str=None):
        if not module:
            return await interact.response.send_message(
                content="> 再読み込みするCogを指定してください"
            )

        try:
            await self.bot.reload_extension(module)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )
        else:
            return await interact.response.send_message(
                content=f"> {module} を再読み込みしました"
            )

    #admin load
    @group.command(name="load", description="ファイルを読み込みます")
    @app_commands.describe(module="読み込むCog")
    @is_owner()
    async def _load(self, interact: discord.Interaction, module: str=None):
        if not module:
            return await interact.response.send_message(
                content="> 読み込むCogを指定してください"
            )

        try:
            await self.bot.load_extension(module)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )
        else:
            return await interact.response.send_message(
                content=f"> {module} を読み込みました"
            )

    #admin unload
    @group.command(name="unload", description="ファイルをunloadします")
    @app_commands.describe(module="unloadするCog")
    @is_owner()
    async def _unload(self, interact: discord.Interaction, module: str=None):
        if not module:
            return await interact.response.send_message(
                content="> unloadするCogを指定してください"
            )

        try:
            await self.bot.unload_extension(module)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )
        else:
            return await interact.response.send_message(
                content=f"> {module} をunloadしました"
            )

#setup
async def setup(bot):
    if not hasattr(bot, "twitter"):
        bot.twitter = Twitter(
            auth=OAuth(
                os.environ["TWITTER_ACCESS"],
                os.environ["TWITTER_ACCESS_SECRET"],
                os.environ["TWITTER_API"],
                os.environ["TWITTER_API_SECRET"]
            )
        )
    if not hasattr(bot, "twitter_media"):
        bot.twitter_media = Twitter(
            domain="upload.twitter.com",
            auth=OAuth(
                os.environ["TWITTER_ACCESS"],
                os.environ["TWITTER_ACCESS_SECRET"],
                os.environ["TWITTER_API"],
                os.environ["TWITTER_API_SECRET"]
            )
        )

    await bot.add_cog(mido_slash_admin(bot))
