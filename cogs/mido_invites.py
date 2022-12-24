import discord
from discord import app_commands
from discord.ext import commands

class meta_invites(commands.CogMeta):
    def __init__(self):
        super().__init__(
            group_name="invites",
            group_description="招待関連の設定です"
        )

@app_commands.guild_only()
class mido_invites(commands.GroupCog, metaclass=meta_invites):

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    #check_cp
    def check_cp(self, target):
        gp = target.guild_permissions
        if gp.administrator:
            return True
        if gp.manage_guild:
            return True
        if gp.create_instant_invite:
            return True
        return False

    #invite toggle
    @app_commands.command(
        name="toggle",
        description="招待の有効化/無効化を設定します"
    )
    @app_commands.describe(
        value="変更する値",
        reason="理由"
    )
    @app_commands.guild_only()
    async def _toggle_invite(self, interact: discord.Interaction, value: bool=None, reason: str=None):
        if not check_cp(interact.guild.me):
            return await interact.response.send_message(
                content="> 権限が不足しています"
            )
        if not check_cp(interact.user):
            return await interact.response.send_message(
                content="> 権限が不足しています"
            )

        try:
            await interact.guild.edit(
                invites_disabled=value,
                reason=reason
            )
        except Exception as exc:
            return await interact.response.send_message(
                content=f"> エラー \n```py\n{exc}\n```"
            )
        else:
            return await interact.response.send_message(
                content=f"> 招待URLの使用を{'有効' if not value else '無効'}化しました"
            )

async def setup(bot):
    await bot.add_cog(mido_invites(bot))
