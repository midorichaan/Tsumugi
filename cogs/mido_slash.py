import discord
from discord import app_commands
from discord.ext import commands

import time
from lib import views, utils

class mido_slash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #ping command
    @app_commands.command(
        name="ping",
        description="BotのPingを返します"
    )
    async def _ping(self, interact: discord.Interaction):
        msg_time = time.perf_counter()

        msg = await interact.response.send_message(
            "> Pinging...",
            ephemeral=True
        )

        ws = round(self.bot.latency * 1000, 2)
        ping = round(time.perf_counter() - msg_time, 3) * 1000

        await interact.edit_original_message(
            content=f"> 🏓Pong! \nPing: {ping}ms \nWebSocket: {ws}ms"
        )

    #punish
    @app_commands.command(
        name="punish",
        description="指定ユーザーを処罰します"
    )
    @app_commands.describe(target="処罰を行うユーザー")
    async def _punish(self, interact: discord.Interaction, target: str=None, reason: str=None):
        if not target:
            return await interact.response.send_message(
                content=f"> 対象ユーザーを指定してください"
            )
        if not reason:
            reason = None

        try:
            interact.bot = interact.client or self.bot
            target = await utils.FetchUserConverter().convert(interact, str(target))
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> メンバー {target} は見つかりませんでした \n```py\n{exc}\n```"
            )

        drop = views.PunishmentDropdown()
        view = views.BasicView().add_item(drop)

        try:
            await interact.response.send_message(
                content="> 処罰の種類を選択してください",
                view=view
            )

            b = await view.wait()
            if b:
                return await interact.response.send_message(
                    content="> タイムアウトしました、最初からやり直してください"
                )

            if drop._value == "punish-kick":
                try:
                    await interact.guild.kick(target, reason=reason)
                except:
                    return await interact.response.send_message(
                        content=f"> メンバーをKickできませんでした"
                    )
                else:
                    return await interact.response.send_message(
                        content=f"> {target} ({target.id})をサーバーからKickしました"
                    )
            elif drop._value == "punish-ban":
                try:
                    await interact.guild.ban(target, reason=reason)
                except:
                    return await interact.response.send_message(
                        content=f"> メンバーをBanできませんでした"
                    )
                else:
                    return await interact.response.send_message(
                        content=f"> {target} ({target.id})をサーバーからBanしました"
                    )
            elif drop._value == "punish-timeout":
                pass
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )

async def setup(bot):
    await bot.add_cog(mido_slash(bot))
