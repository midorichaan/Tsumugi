import discord
from discord import ui
from typing import Union

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
            )
        ]
        self.target = target
        self.reason = reason

        super().__init__(
            placeholder="処罰の種類を選択してください",
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
                return await interact.edit_original_response(
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
                return await interact.edit_original_response(
                    content=f"> {self.target} をBanできませんでした",
                    view=None
                )
        elif str(self.values[0]) == "punish-timeout":
            pass
    
class BasicView(ui.View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
