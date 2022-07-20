import discord
from discord.ext import commands

import traceback
from lib import utils

class mido_events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #on_shard_connect
    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id: int) -> None:
        self.bot.logger.info(
            f"SESSION: Shard ID {shard_id} has successfully connected to Discord"
        )
        self.bot.instance["shards"][shard_id] = 1

    #on_shard_disconnect
    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id: int) -> None:
        self.bot.logger.warning(
            f"SESSION: Shard ID {shard_id} has disconnected from Discord"
        )
        self.bot.instance["shards"][shard_id] = 0

    #on_shard_ready
    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id: int) -> None:
        self.bot.logger.info(
            f"SESSION: Shard ID {shard_id} has become ready"
        )
        self.bot.instance["shards"][shard_id] = 2

    #on_shard_resumed
    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id: int) -> None:
        self.bot.logger.info(
            f"SESSION: Shard ID {shard_id} has resumed"
        )
        self.bot.instance["shards"][shard_id] = 2

    #on_resumed
    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        self.bot.logger.info(
            "SESSION: Session has resumed"
        )
        self.bot.instance["session"] = 1

    #on_disconnect
    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        self.bot.logger.warning(
            "SESSION: Successfully disconnected to Discord"
        )
        self.bot.instance["session"] = 0

    #on_connect
    @commands.Cog.listener()
    async def on_connect(self) -> None:
        self.logger.info(
            "Successfully connected to Discord"
        )

        for i in range(self.shard_count):
            self.bot.instance["shards"][i] = 0
        self.bot.instance["session"] = 1

    #on_command
    @commands.Cog.listener()
    async def on_command(self, ctx) -> None:
        if isinstance(ctx.channel, discord.DMChannel):
            format = f"COMMAND: {ctx.author} ({ctx.author.id}) -> {ctx.message.content} @DM"
            self.bot.logger.info(format)
        else:
            format = f"COMMAND: {ctx.author} ({ctx.author.id}) -> {ctx.message.content} @{ctx.channel} ({ctx.channel.id}) - {ctx.guild} ({ctx.guild.id})"
            self.bot.logger.info(format)

    #on_command_error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc) -> None:
        traceback_exc = ''.join(
            traceback.TracebackException.from_exception(exc).format()
        )
        format = ""

        self.bot.instance["exception"] = {
            "error": exc,
            "traceback": traceback_exc,
            "context": ctx
        }

        if isinstance(ctx.channel, discord.DMChannel):
            format = f"ERROR: {ctx.author} ({ctx.author.id}) -> {exc} @DM"
        else:
            format = f"ERROR: {ctx.author} ({ctx.author.id}) -> {exc} @{ctx.channel} ({ctx.channel.id}) - {ctx.guild} ({ctx.guild.id})"

        self.bot.logger.warning(format)
        await utils.reply_or_send(
            ctx,
            content=f"> エラー \n```py\n{exc}\n```"
        )

    #on_interact
    @commands.Cog.listener()
    async def on_interaction(self, interact: discord.Interaction):
        if interact.type == discord.InteractionType.ping:
            pass
        elif interact.type == discord.InteractionType.application_command:
            format = ""

            if isinstance(interact.channel, discord.DMChannel):
                format = f"APPCMD: {interact.user} ({interact.user.id}) - {interact.id} → {interact.command} @{interact.user} ({interact.user.id})"
            else:
                format = f"APPCMD: {interact.user} ({interact.user.id}) - {interact.id} → {interact.command} @{interact.guild} ({interact.guild.id})"
            self.bot.logger.info(format)
        elif interact.type == discord.InteractionType.component:
            pass
        elif interact.type == discord.InteractionType.autocomplete:
            pass
        elif interact.type == discord.InteractionType.modal_submit:
            pass

#setup
async def setup(bot):
    await bot.add_cog(mido_events(bot))
