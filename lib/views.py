import discord
from discord import ui
from typing import Union

from . import time

class PunishmentDropdown(ui.Select):

    def __init__(self, target: Union[discord.Member, discord.User]=None, *, reason: str=None):
        options = [
            discord.SelectOption(
                label="punish-kick",
                description="メンバーをサーバーからKickします",
                emoji="🦶"
            ),
            discord.SelectOption(
                label="punish-ban",
                description="メンバーをサーバーからBanします",
                emoji="⚒"
            ),
            discord.SelectOption(
                label="punish-timeout",
                description="メンバーをタイムアウトします",
                emoji="📢"
            ),
            discord.SelectOption(
                label="punish-unban",
                description="メンバーのBanを解除します",
                emoji="⚙"
            )
        ]
        self.target = target
        self.reason = reason

        super().__init__(
            placeholder="種類を選択してください",
            min_values=1,
            max_values=1,
            options=options,
        )

    #callback
    async def callback(self, interact: discord.Interaction):
        await interact.response.defer(ephemeral=True, thinking=True)
        if str(self.values[0]) == "punish-kick":
            try:
                await interact.guild.kick(
                    self.target,
                    reason=self.reason
                )
            except:
                await interact.edit_original_response(
                    content=f"> {self.target} をKickできませんでした",
                    view=None
                )
        elif str(self.values[0]) == "punish-ban":
            try:
                await interact.guild.ban(
                    self.target,
                    reason=self.reason
                )
            except:
                await interact.edit_original_response(
                    content=f"> {self.target} をBanできませんでした",
                    view=None
                )
        elif str(self.values[0]) == "punish-timeout":
            modal = TimeoutModal(
                title="タイムアウト期間",
                member=self.target,
                reason=self.reason
            )
            try:
                await interact.response.send_modal(modal)
            except:
                await interact.edit_original_response(
                    content=f"> 処理中にエラーが発生しました",
                    view=None
                )
        elif str(self.values[0]) == "punish-unban":
            try:
                banlist = [i.user.id async for i in interact.guild.bans(limit=None)]
                if self.target.id in banlist:
                    await interact.guild.unban(self.target, reason=self.reason)
                else:
                    await interact.edit_original_response(
                        content=f"> {self.target} はBanされていません",
                        view=None
                    )
            except:
                await interact.edit_original_response(
                    content=f"> {self.target} のBanを解除できませんでした",
                    view=None
                )
        self.stop()

class TimeoutModal(ui.Modal):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member = kwargs.get("member")
        self.reason = kwargs.get("reason")
    
    duration = ui.TextInput(
        custom_id="timeout-duration",
        label="ここに期間を入力してください"
        placeholder=None,
        style=discord.TextStyle.long,
        required=True
    )

    async def on_submit(self, interact: discord.Interaction):
        try:
            conv = await time.ShortTime.convert(interact, str(self.duration.value))
        except:
            await interact.edit_original_response(
                content=f"> 時刻の変換中にエラーが発生しました",
                view=None
            )
        else:
            try:
                await self.member.timeout(conv, reason=self.reason)
            except:
                await interact.edit_original_response(
                    content=f"> メンバーのタイムアウト中にエラーが発生しました",
                    view=None
                )
            else:
                await interact.edit_original_message(
                    content=f"> {self.member} をタイムアウトしました \n期間: {discord.utils.format_dt(conv, style='F')}"
                )
        finally:
            self.stop()

    async def on_error(self, interact: discord.Interaction, error: Exception):
        try:
            await interact.edit_original_response(
                content=f"> エラー \n```py\n{error}\n```",
                view=None
            )
        except:
            pass
        finally:
            self.stop()
    
class BasicView(ui.View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
