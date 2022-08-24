import asyncio
import copy
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
        if hasatrr(interact, "client"):
            new_interact.bot = interact.client
            
        if argument.isdigit():
            ret = new_interact.bot.get_user(int(argument))
            if not ret:
                try:
                    return await new_interact.bot.fetch_user(int(argument))
                except:
                    return None
        try:
            return await commands.MemberConverter().convert(new_ctx, argument)
        except:
            try:
                return await commands.UserConverter().convert(new_ctx, argument)
            except:
                return None
