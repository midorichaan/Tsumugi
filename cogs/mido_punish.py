import discord
from discord.ext import commands

from lib import utils

class mido_punish(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._allowed_guilds = [
            701131006698192916
        ]

    async def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            return False

        if ctx.guild.id in self._allowed_guilds:
            return True
        return False

    #ban
    @commands.command(
        name="ban",
        aliases=["gg", "goodbye"],
        description="メンバーをサーバーからBanします"
    )
    @commands.has_permissions(
        kick_members=True,
        ban_members=True,
        moderate_members=True
    )
    @commands.bot_has_permissions(
        kick_members=True,
        ban_members=True,
        moderate_members=True
    )
    async def _ban(self, ctx: commands.Context, target: utils.FetchUserConverter=None, *, reason: str=None):
        if not target:
            return await utils.reply_or_send(ctx, content="> ユーザーを指定してください。")

        if not utils.check_hierarchy(ctx, target):
            return await utils.reply_or_send(ctx, content=f"> このユーザーはBanできません。")

        if not reason:
            reason = "理由なし"
        reason = f"{ctx.author}: {reason}"

        try:
            await ctx.guild.ban(target, reason=reason)
        except Exception as exc:
            return await utils.reply_or_send(ctx, content=f"> エラー \n```py\n{exc}\n```")
        else:
            return await utils.reply_or_send(ctx, content=f"> {target} をこのサーバーからBanしました。 \n理由: {reason}")

    #kick
    @commands.command(
        name="kick",
        description="メンバーをサーバーからKickします。"
    )
    @commands.has_permissions(
        kick_members=True,
        ban_members=True,
        moderate_members=True
    )
    @commands.bot_has_permissions(
        kick_members=True,
        ban_members=True,
        moderate_members=True
    )
    async def _kick(self, ctx: commands.Context, target: utils.FetchUserConverter=None, *, reason: str=None):
        if not target:
            return await utils.reply_or_send(ctx, content=f"> ユーザーを指定してください。")

        if not utils.check_hierarchy(ctx, target):
            return await utils.reply_or_send(ctx, content=f"> このユーザーはKickできません。")

        if not reason:
            reason = "理由なし"
        reason = f"{ctx.author}: {reason}"

        try:
            await ctx.guild.kick(target, reason=reason)
        except Exception as exc:
            return await utils.reply_or_send(ctx, content=f"> エラー \n```py\n{exc}\n```")
        else:
            return await utils.reply_or_send(ctx, content=f"> {target} をこのサーバーからKickしました。 \n理由: {reason}")

    #timeout
    @commands.command(
        name="timeout",
        description="メンバーをタイムアウトします"
    )
    @commands.has_permissions(
        kick_members=True,
        ban_members=True,
        moderate_members=True
    )
    @commands.bot_has_permissions(
        kick_members=True,
        ban_members=True,
        moderate_members=True
    )
    async def _timeout(
        self, 
        ctx: commands.Context, 
        target: utils.FetchUserConverter=None, 
        duration: utils.ShortTime=None,
        *,
        reason: str=None
    ):
        if not target:
            return await utils.reply_or_send(ctx, content=f"> ユーザーを指定してください。")

        if not utils.check_hierarchy(ctx, target):
            return await utils.reply_or_send(ctx, content=f"> このユーザーはTimeoutできません。")

        if not reason:
            reason = "理由なし"
        reason = f"{ctx.author}: {reason}"

        try:
            await target.timeout(duration, reason=reason)
        except Exception as exc:
            return await utils.reply_or_send(ctx, content=f"> エラー \n```py\n{exc}\n```")
        else:
            return await utils.reply_or_send(ctx, content=f"> {target} をこのサーバーからKickしました。 \n理由: {reason}")

async def setup(bot):
    await bot.add_cog(mido_punish(bot))
