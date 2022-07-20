import discord
from discord import app_commands
from discord.ext import commands

class mido_slash_admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #group instance
    group = app_commands.Group(
        name="admin",
        description="管理者用コマンド"
    )

    #admin reload
    @group.command(name="reload", description="ファイルの再読み込みを行います")
    @app_commands.describe(module="再読み込みするCog")
    async def _reload(self, interact: discord.Interaction, module: str=None):
        if not module:
            return await interact.response.send_message(
                content="> 再読み込みするCogを指定してください",
                ephemeral=True
            )

        try:
            await self.bot.reload_extension(module)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```",
                ephemeral=True
            )
        else:
            return await interact.response.send_message(
                content=f"> {module} を再読み込みしました",
                ephemeral=True
            )

    #admin load
    @group.command(name="load", description="ファイルを読み込みます")
    @app_commands.describe(module="読み込むCog")
    async def _load(self, interact: discord.Interaction, module: str=None):
        if not module:
            return await interact.response.send_message(
                content="> 読み込むCogを指定してください",
                ephemeral=True
            )

        try:
            await self.bot.load_extension(module)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```",
                ephemeral=True
            )
        else:
            return await interact.response.send_message(
                content=f"> {module} を読み込みました",
                ephemeral=True
            )

    #admin unload
    @group.command(name="unload", description="ファイルをunloadします")
    @app_commands.describe(module="unloadするCog")
    async def _unload(self, interact: discord.Interaction, module: str=None):
        if not module:
            return await interact.response.send_message(
                content="> unloadするCogを指定してください",
                ephemeral=True
            )

        try:
            await self.bot.unload_extension(module)
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```",
                ephemeral=True
            )
        else:
            return await interact.response.send_message(
                content=f"> {module} をunloadしました",
                ephemeral=True
            )

#setup
async def setup(bot):
    await bot.add_cog(mido_slash_admin(bot))
