import asyncio
import copy
import discord
import re
import subprocess
from discord.ext import commands

#get_status
def get_status(member):
    status = str(member.status)
    if status == "online":
        return f"💚オンライン"
    elif status == "idle":
        return f"🧡退席中"
    elif status == "dnd":
        return f"❤取り込み中"
    elif status == "offline":
        return f"🖤オフライン"
    else:
        return f"💔不明"

#reply_or_send
async def reply_or_send(ctx, *args, **kwargs):
    try:
        return await ctx.reply(*args, **kwargs)
    except:
        try:
            return await ctx.send(*args, **kwargs)
        except:
            try:
                return await ctx.author.send(*args, **kwargs)
            except:
                pass

#remove ```
def cleanup_code(content):
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')

#create shell process
async def run_process(ctx, command):
    try:
        process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = await process.communicate()
    except NotImplementedError:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = await ctx.bot.loop.run_in_executor(None, process.communicate)

    return [output.decode() for output in result]

#fetchuserconverter
class FetchUserConverter(commands.Converter):
    async def convert(self, ctx, argument):
        new_ctx = copy.copy(ctx)
        if hasatrr(ctx, "client"):
            new_ctx.bot = ctx.client
            
        if argument.isdigit():
            ret = new_ctx.bot.get_user(int(argument))
            if not ret:
                try:
                    return await new_ctx.bot.fetch_user(int(argument))
                except:
                    return None
        try:
            return await commands.MemberConverter().convert(new_ctx, argument)
        except:
            try:
                return await commands.UserConverter().convert(new_ctx, argument)
            except:
                return None

#fetchuserconverter
class FetchUserSlashConverter(commands.Converter):
    async def convert(self, interact, argument):
        new_interact = copy.copy(interact)
            
        if argument.isdigit():
            ret = new_interact.client.get_user(int(argument))
            if not ret:
                try:
                    return await new_interact.client.fetch_user(int(argument))
                except:
                    return None
        try:
            return await MemberConverter().convert(new_interact, argument)
        except:
            try:
                return await UserConverter().convert(new_interact, argument)
            except:
                return None

class MemberConverter(commands.IDConverter[discord.Member]):
    """Converts to a :class:`~discord.Member`.

    All lookups are via the local guild. If in a DM context, then the lookup
    is done by the global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name#discrim
    4. Lookup by name
    5. Lookup by nickname

    .. versionchanged:: 1.5
         Raise :exc:`.MemberNotFound` instead of generic :exc:`.BadArgument`

    .. versionchanged:: 1.5.1
        This converter now lazily fetches members from the gateway and HTTP APIs,
        optionally caching the result if :attr:`.MemberCacheFlags.joined` is enabled.
    """

    async def query_member_named(self, guild: discord.Guild, argument: str):
        cache = guild._state.member_cache_flags.joined
        if len(argument) > 5 and argument[-5] == '#':
            username, _, discriminator = argument.rpartition('#')
            members = await guild.query_members(username, limit=100, cache=cache)
            return discord.utils.get(members, name=username, discriminator=discriminator)
        else:
            members = await guild.query_members(argument, limit=100, cache=cache)
            return discord.utils.find(lambda m: m.name == argument or m.nick == argument, members)

    async def query_member_by_id(self, bot, guild: discord.Guild, user_id: int):
        ws = bot._get_websocket(shard_id=guild.shard_id)
        cache = guild._state.member_cache_flags.joined
        if ws.is_ratelimited():
            # If we're being rate limited on the WS, then fall back to using the HTTP API
            # So we don't have to wait ~60 seconds for the query to finish
            try:
                member = await guild.fetch_member(user_id)
            except discord.HTTPException:
                return None

            if cache:
                guild._add_member(member)
            return member

        # If we're not being rate limited then we can use the websocket to actually query
        members = await guild.query_members(limit=1, user_ids=[user_id], cache=cache)
        if not members:
            return None
        return members[0]

    async def convert(self, ctx, argument: str) -> discord.Member:
        bot = ctx.client
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]{15,20})>$', argument)
        guild = ctx.guild
        result = None
        user_id = None

        if match is None:
            # not a mention...
            if guild:
                result = guild.get_member_named(argument)
            else:
                result = _get_from_guilds(bot, 'get_member_named', argument)
        else:
            user_id = int(match.group(1))
            if guild:
                result = guild.get_member(user_id) or _utils_get(ctx.message.mentions, id=user_id)
            else:
                result = _get_from_guilds(bot, 'get_member', user_id)

        if not isinstance(result, discord.Member):
            if guild is None:
                raise commands.MemberNotFound(argument)

            if user_id is not None:
                result = await self.query_member_by_id(bot, guild, user_id)
            else:
                result = await self.query_member_named(guild, argument)

            if not result:
                raise commands.MemberNotFound(argument)

        return result

class UserConverter(commands.IDConverter[discord.User]):
    """Converts to a :class:~discord.User.

    All lookups are via the global user cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name#discrim
    4. Lookup by name

    .. versionchanged:: 1.5
         Raise :exc:.UserNotFound instead of generic :exc:.BadArgument

    .. versionchanged:: 1.6
        This converter now lazily fetches users from the HTTP APIs if an ID is passed
        and it's not available in cache.
    """

    async def convert(self, ctx, argument: str) -> discord.User:
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]{15,20})>$', argument)
        result = None
        state = ctx._state

        if match is not None:
            user_id = int(match.group(1))
            result = ctx.client.get_user(user_id) or _utils_get(ctx.message.mentions, id=user_id)
            if result is None:
                try:
                    result = await ctx.client.fetch_user(user_id)
                except discord.HTTPException:
                    raise commands.UserNotFound(argument) from None

            return result  # type: ignore

        arg = argument

        # Remove the '@' character if this is the first character from the argument
        if arg[0] == '@':
            # Remove first character
            arg = arg[1:]

        # check for discriminator if it exists,
        if len(arg) > 5 and arg[-5] == '#':
            discrim = arg[-4:]
            name = arg[:-5]
            predicate = lambda u: u.name == name and u.discriminator == discrim
            result = discord.utils.find(predicate, state._users.values())
            if result is not None:
                return result

        predicate = lambda u: u.name == arg
        result = discord.utils.find(predicate, state._users.values())

        if result is None:
            raise commands.UserNotFound(argument)

        return result
