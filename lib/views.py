import discord
from discord import ui

class PunishmentDropdown(ui.Select):

    def __init__(self):
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

        super().__init__(
            placeholder="処罰の種類を選択してください",
            min_values=1,
            max_values=1,
            options=options
        )
        self._value = None

    #callback
    async def callback(self, interact: discord.Interaction):
        self._value = self.values[0]
        return self.values
    
class BasicView(ui.View):

    def __init__(self):
        super().__init__()
