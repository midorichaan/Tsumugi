import discord
from discord import app_commands
from discord.ext import commands

import time
from lib import views, utils

class mido_slash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #_check_permission
    def _check_permission(self, interact: discord.Interaction):
        result = ["", []]

        gp = interact.guild.me.guild_permissions
        if not gp.ban_members:
            result[1].append("メンバーをBan")
        if not gp.kick_members:
            result[1].append("メンバーをKick")
        if not gp.moderate_members:
            result[1].append("メンバーをタイムアウト")
        result[0] = "bot-missing"

        mp = interact.user.guild_permissions
        if not mp.ban_members:
            result[1].append("メンバーをBan")
        if not mp.kick_members:
            result[1].append("メンバーをKick")
        if not mp.moderate_members:
            result[1].append("メンバーをタイムアウト")
        result[0] = "user-missing"
        return result

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

        await interact.edit_original_response(
            content=f"> 🏓Pong! \nPing: {ping}ms \nWebSocket: {ws}ms"
        )

    #punish
    @app_commands.command(
        name="punish",
        description="指定ユーザーを処罰します"
    )
    @app_commands.describe(target="処罰を行うユーザー", reason="理由")
    async def _punish(self, interact: discord.Interaction, target: str=None, reason: str=None):
        if isinstance(interact.channel, discord.DMChannel):
            return await interact.response.send_message(
                content="> DMでは使用できません",
            )

        check = self._check_permission(interact)
        if str(check[0]) == "bot-missing" and check[1] != []:
            perm = ", ".join([f"`{i}`" for i in check[1]])
            return await interact.response.send_message(
                content=f"> Botに{perm}の権限が不足しています"
            )
        if str(check[0]) == "user-missing" and check[1] != []:
            perm = ", ".join([f"`{i}`" for i in check[1]])
            return await interact.response.send_message(
                content=f"> {perm}の権限が不足しています"
            )

        if not target:
            return await interact.response.send_message(
                content=f"> 対象ユーザーを指定してください"
            )
        if not reason:
            reason = None

        try:
            target = await utils.FetchUserSlashConverter().convert(interact, str(target))
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )

        drop = views.PunishmentDropdown(target, reason=reason)
        view = views.BasicView(timeout=30.0).add_item(drop)

        try:
            await interact.response.send_message(
                content="> 処罰の種類を選択してください",
                view=view
            )

            b = await view.wait()
            if b:
                return await interact.edit_original_response(
                    content="> タイムアウトしました、最初からやり直してください",
                    view=None
                )
        except Exception as exc:
            return await interact.edit_original_response(
                content=f"> エラー \n```py\n{exc}\n```",
                view=None
            )

async def setup(bot):
    await bot.add_cog(mido_slash(bot))
