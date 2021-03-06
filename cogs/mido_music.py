import discord
import functools
from discord.ext import commands

import asyncio
import os
import youtube_dl
import datetime
import random

from dotenv import load_dotenv
from apiclient.discovery import build
from lib import utils as util, paginator

#load .env file
load_dotenv()

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': 'musics/%(id)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'geo-bypass': True,
    'verbose': False
}

ffmpeg_options = {
    'before_options': '-loglevel fatal -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

class mido_music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
       # self.youtube = build("youtube", "v3", developerKey=os.environ["YOUTUBE_KEY"])

    #get_data
    async def get_data(self, ctx, key, download=False):
        loop = self.bot.loop or asyncio.get_event_loop()

        try:
            data = await loop.run_in_executor(None, functools.partial(self.ytdl.extract_info, key, download=download))
        except Exception as exc:
            raise exc

        return data

    #get_info
    async def get_info(self, ctx, url, download=False):
        data = await self.get_data(ctx, url, download)

        result = {
            "type": "Download" if download else "Stream",
            "url": data.get("url", "unknown"),
            "id": data.get("id", "unknown"),
            "webpage_url": data.get("webpage_url", "unknown"),
            "title": data.get("title", "unknown"),
            "thumbnail": data.get("thumbnail", "unknown"),
            "uploader": data.get("uploader", "unknown"),
            "uploader_url": data.get("uploader_url", "unknown"),
            "request": ctx.author.id
        }

        return result

    #shuffle
    @commands.command(name="shuffle", description="???????????????????????????????????????")
    async def shuffle(self, ctx):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.author.voice:
            if ctx.guild.voice_client:
                if ctx.author.voice.channel == ctx.guild.voice_client.channel:
                    if self.bot.queue.get(ctx.guild.id, None):
                        for i in range(5):
                            random.shuffle(self.bot.queue[ctx.guild.id])
                        return await msg.edit(content="> ???????????????????????????")
                    else:
                        return await msg.edit(content="> ?????????????????????????????????")
                else:
                    return await msg.edit(content=f"> ???????????????????????????????????????????????????????????????")
            else:
                return await msg.edit(content=f"> ???????????????????????????????????????????????????????????????????????????")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

    #stop
    @commands.command(name="stop", description="????????????????????????????????????????????????????????????????????????????????????????????????????????????", aliases=["leave"])
    async def stop(self, ctx):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.author.voice:
            if ctx.guild.voice_client:
                if ctx.author.voice.channel == ctx.guild.voice_client.channel:
                    try:
                        await ctx.guild.voice_client.disconnect()

                        try:
                            del self.bot.queue[ctx.guild.id]
                            del self.bot.loop_queue[ctx.guild.id]
                        except:
                            pass
                    except Exception as exc:
                        return await msg.edit(content=f"> ????????? \n```\n{exc}\n```")
                    else:
                        await msg.edit(content=f"> ????????????????????????????????????????????????????????????????????????")
                else:
                    return await msg.edit(content=f"> ???????????????????????????????????????????????????????????????")
            else:
                return await msg.edit(content=f"> ???????????????????????????????????????????????????????????????????????????")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

    #play
    @commands.command(name="play", aliases=["p"], description="???????????????????????????")
    async def play(self, ctx, query:str=None):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.author.voice:
            if not ctx.guild.voice_client:
                try:
                    vc = await ctx.author.voice.channel.connect()
                except Exception as exc:
                    return await msg.edit(content=f"> ????????? \n```\n{exc}\n```")
                else:
                    await msg.edit(content=f"> {vc.channel.name}??????????????????????????????????????????????????????...")
            else:
                await msg.edit(content="> ?????????????????????????????????...")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

        if ctx.guild.voice_client.is_paused():
            ctx.guild.voice_client.resume()
            return await msg.edit(content="> ???????????????????????????")

        if not query:
            await msg.edit(content="> ???????????????/URL??????????????????????????????")

            try:
                message = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30.0)
            except asyncio.TimeoutError:
                return await msg.edit(content="> 30??????????????????????????????????????????????????????")
            else:
                await msg.edit(content="> ?????????????????????????????????....")
                query = message.content

        if query.startswith("download:"):
            try:
                data = await self.get_data(ctx, query[9:], True)
            except Exception as exc:
                return await msg.edit(content=f"> ????????? \n```\n{exc}\n```")
            else:
                if data.get("_type", None) == "playlist":
                    try:
                        data = await self.get_info(ctx, f"https://youtu.be/{data['entries'][0]['id']}", True)
                    except Exception as exc:
                        return await msg.edit(content=f"> ????????? \n```py\n{exc}\n```")
                    else:
                        if self.bot.queue.get(ctx.guild.id, None):
                            self.bot.queue[ctx.guild.id] = self.bot.queue[ctx.guild.id] + [data]
                            return await msg.edit(content=f"> ????????????{data['title']}?????????????????????")
                        else:
                            self.bot.queue[ctx.guild.id] = [data]
                            await msg.edit(content=f"> {data['title']}?????????????????????")
                            self.bot.loop.create_task(self._play(ctx))
                else:
                    if self.bot.queue.get(ctx.guild.id, None):
                        self.bot.queue[ctx.guild.id] = self.bot.queue[ctx.guild.id] + [data]
                        return await msg.edit(content=f"> ????????????{ret['title']}?????????????????????")
                    else:
                        self.bot.queue[ctx.guild.id] = [data]
                        await msg.edit(content=f"> {data['title']}?????????????????????")
                        self.bot.loop.create_task(self._play(ctx))
        else:
            try:
                data = await self.get_data(ctx, query, False)
            except Exception as exc:
                return await msg.edit(content=f"> ????????? \n```\n{exc}\n```")

            lists = []

            #from sina () maybe only youtube
            if data.get("_type", None) == "playlist":
                if len(data["entries"]) >= 5:
                    lists.append(self.get_info(ctx, f"https://www.youtube.com/watch?v={data['entries'][0]['id']}", False))
                else:    
                    for i in data["entries"]:
                        lists.append(self.get_info(ctx, f"https://www.youtube.com/watch?v={i['id']}", False))

                try:
                    ret = [r for r in await asyncio.gather(*lists) if r]
                except Exception as exc:
                    return await msg.edit(content=f"> ????????? \n```\n{exc}\n```")
                else:
                    if not ret:
                        return await msg.edit(content="> ????????????????????????????????????????????????")

                if self.bot.queue.get(ctx.guild.id, None):
                    self.bot.queue[ctx.guild.id] = self.bot.queue[ctx.guild.id] + ret
                    return await msg.edit(content=f"> ????????????{len(ret)}?????????????????????????????????")
                else:
                    self.bot.queue[ctx.guild.id] = ret
                    await msg.edit(content=f"> ???????????????????????????{len(ret)}?????????????????????????????????")
                    self.bot.loop.create_task(self._play(ctx))
            else:
                ret = await self.get_info(ctx, f"https://www.youtube.com/watch?v={data['id']}", False)

                if self.bot.queue.get(ctx.guild.id, None):
                    self.bot.queue[ctx.guild.id] = self.bot.queue[ctx.guild.id] + [ret]
                    return await msg.edit(content=f"> ????????????{ret['title']}?????????????????????")
                else:
                    self.bot.queue[ctx.guild.id] = [ret]
                    await msg.edit(content=f"> {ret['title']}?????????????????????")
                    self.bot.loop.create_task(self._play(ctx))

    #skip
    @commands.command(name="skip", description="??????????????????????????????")
    async def skip(self, ctx):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.author.voice:
            if ctx.guild.voice_client:
                if not ctx.guild.voice_client.channel == ctx.author.voice.channel:
                    return await msg.edit(content="> ?????????????????????????????????????????????????????????????????????")

                if ctx.guild.voice_client.is_playing():
                    loop = self.bot.loop_queue[ctx.guild.id]
                    self.bot.loop_queue[ctx.guild.id] = False
                    ctx.guild.voice_client.stop()
                    self.bot.loop_queue[ctx.guild.id] = loop
                    return await msg.edit(content="> ??????????????????????????????")
                else:
                    return await msg.edit(content=f"> ??????????????????????????????????????????")
            else:
                return await msg.edit(content="> ?????????????????????????????????????????????????????????")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

    #pause
    @commands.command(name="pause", description="???????????????????????????????????????")
    async def pause(self, ctx):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.author.voice:
            if ctx.guild.voice_client:
                if not ctx.guild.voice_client.channel == ctx.author.voice.channel:
                    return await msg.edit(content="> ?????????????????????????????????????????????????????????????????????")

                if ctx.guild.voice_client.is_playing():
                    ctx.guild.voice_client.pause()
                    return await msg.edit(content="> ??????????????????????????????")
                else:
                    return await msg.edit(content=f"> ??????????????????????????????????????????")
            else:
                return await msg.edit(content="> ?????????????????????????????????????????????????????????")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

    #volume
    @commands.command(name="volume", aliases=["vol"], description="???????????????????????????", usage="rsp!volume <volume>")
    async def volume(self, ctx, vol: float=None):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.author.voice:
            if ctx.guild.voice_client:
                if not ctx.guild.voice_client.channel == ctx.author.voice.channel:
                    return await msg.edit(content="> ?????????????????????????????????????????????????????????????????????")

                if not ctx.guild.voice_client.is_playing():
                    return await msg.edit(content="> ????????????????????????????????????")

                if not vol:
                    return await msg.edit(content="> ???????????????????????????")

                ctx.guild.voice_client.source.volume = vol/100.0
                return await msg.edit(content=f"> ?????????{vol}??????????????????")
            else:
                return await msg.edit(content="> ?????????????????????????????????????????????????????????")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

    #nowplaying
    @commands.command(name="nowplaying", aliases=["np"], description="?????????????????????????????????????????????")
    async def nowplaying(self, ctx):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.guild.voice_client:
            if ctx.guild.voice_client.is_playing():
                queue = self.bot.queue[ctx.guild.id][0]

                e = discord.Embed(title="????Now Playing", color=self.bot.color, timestamp=ctx.message.created_at)
                e.set_thumbnail(url=queue["thumbnail"])
                e.set_footer(text=f"Requested by {self.bot.get_user(queue['request'])}", icon_url=self.bot.get_user(queue["request"]).avatar_url_as(static_format="png"))
                e.add_field(name="???????????????", value=f"[{queue['title']}]({queue['webpage_url']})")
                e.add_field(name="?????????????????????????????????", value=f"[{queue['uploader']}]({queue['uploader_url']})")
                return await msg.edit(content=None, embed=e)
            else:
                return await msg.edit(content="> ????????????????????????????????????")
        else:
            return await msg.edit(content="> ?????????????????????????????????????????????????????????")

    #queue
    @commands.command(name="queue", aliases=["q"], description="??????????????????????????????")
    async def queue(self, ctx):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if not ctx.guild.voice_client:
            return await msg.edit(content="> ?????????????????????????????????????????????????????????")

        if self.bot.queue.get(ctx.guild.id, []) == []:
            return await msg.edit(content="> ?????????????????????????????????????????????")

        e = discord.Embed(title="????Music Queues", description="", color=self.bot.color, timestamp=ctx.message.created_at)
        count = 1
        for i in self.bot.queue[ctx.guild.id]:
            e.description += f"{count}. [{i['title']}]({i['webpage_url']})\n"
            count += 1
        return await msg.edit(content=None, embed=e)

    #loop
    @commands.command(name="loop", aliases=["repeat"], description="???????????????????????????????????????")
    async def loop(self, ctx, loop: bool=None):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if ctx.author.voice:
            if ctx.guild.voice_client:
                if not ctx.guild.voice_client.channel == ctx.author.voice.channel:
                    return await msg.edit(content="> ?????????????????????????????????????????????????????????????????????")

                if not ctx.guild.voice_client.is_playing():
                    return await msg.edit(content="> ????????????????????????????????????")

                if loop:
                    self.bot.loop_queue[ctx.guild.id] = loop
                    return await msg.edit(content=f"> ????????????{loop}???????????????")
                else:
                    if self.bot.loop_queue[ctx.guild.id]:
                        self.bot.loop_queue[ctx.guild.id] = False
                        return await msg.edit(content=f"> ????????????False???????????????")
                    else:
                        self.bot.loop_queue[ctx.guild.id] = True
                        return await msg.edit(content=f"> ????????????True???????????????")
            else:
                return await msg.edit(content="> ?????????????????????????????????????????????????????????")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

    #delete
    @commands.command(aliases=["rm", "del"])
    async def delete(self, ctx, index: int=None):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if isinstance(ctx.channel, discord.DMChannel):
            return await msg.edit(content="> DM????????????????????????")

        if not index:
            return await msg.edit(content="> ?????????????????????????????????????????????")

        if index <= 0:
            return await msg.edit(content="> 1?????????????????????????????????")

        if ctx.author.voice:
            if ctx.guild.voice_client:
                if not ctx.guild.voice_client.channel == ctx.author.voice.channel:
                    return await msg.edit(content="> ?????????????????????????????????????????????????????????????????????")

                q = self.bot.queue.get(ctx.guild.id, None)
                if q is not None:
                    index = index - 1

                    if len(q) <= index:
                        return await msg.edit(content="> ????????????????????????????????????")

                    try:
                        del q[index]
                        return await msg.edit(content=f"> {index + 1}?????????????????????????????????")
                    except Exception as exc:
                        return await msg.edit(content=f"> ????????? \n```py\n{exc}\n```")
                else:
                    return await msg.edit(content="> ?????????????????????????????????")
            else:
                return await msg.edit(content="> ?????????????????????????????????????????????????????????")
        else:
            return await msg.edit(content=f"> ?????????????????????????????????????????????")

    #search
    @commands.command(aliases=["yt", "ytsearch"])
    async def search(self, ctx, *, query: str=None):
        msg = await util.reply_or_send(ctx, content="> ?????????...")

        if not query:
            await msg.edit(content="> ??????????????????????????????????????????")
            try:
                message = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30.0)
            except asyncio.TimeouError:
                return await msg.edit(content="> ?????????????????????????????????")
            else:
                await msg.edit(content="> ?????????????????????...")
                query = message.content

        try:
            querys = self.youtube.search().list(part="snippet", q=query, type="video").execute()
        except Exception as exc:
            return await msg.edit(content=f"> ????????? \n```\n{exc}\n```")
        else:
            items = querys.get("items", None)

            if not items:
                return await msg.edit(content="> ????????????????????????????????????")

            embeds = []

            for i in items:
                e = discord.Embed(title="????Music Search", color=self.bot.color, timestamp=ctx.message.created_at)
                e.set_thumbnail(url=i["snippet"]["thumbnails"]["medium"]["url"])
                e.add_field(name="????????????", value=f"[{i['snippet']['title']}](https://youtube.com/watch?v={i['id']['videoId']})")
                e.add_field(name="??????URL", value=f"https://youtube.com/watch?v={i['id']['videoId']}")
                e.add_field(name="??????", value=f"```\n{i['snippet']['description']}\n```", inline=False)
                e.add_field(name="?????????????????????", value=datetime.datetime.strptime(i["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d %H:%M:%S"))
                e.add_field(name="?????????????????????????????????", value=f"[{i['snippet']['channelTitle']}](https://youtube.com/channel/{i['snippet']['channelId']})")
                e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url_as(static_format="png"))
                embeds.append(e)

            await msg.delete()
            page = paginator.EmbedPaginator(ctx, entries=embeds, timeout=30.0)
            await page.paginate()

    #_play
    async def _play(self, ctx, vol=0.5, src=None):
        if not self.bot.loop_queue.get(ctx.guild.id, None):
            self.bot.loop_queue[ctx.guild.id] = False

        vol = vol
        while self.bot.queue[ctx.guild.id]:
            if self.bot.queue[ctx.guild.id][0]["type"] == "Stream":
                src = discord.FFmpegPCMAudio(self.bot.queue[ctx.guild.id][0]["url"], options=ffmpeg_options)
            elif self.bot.queue[ctx.guild.id][0]["type"] == "Download":
                src = discord.FFmpegPCMAudio(f"musics/{self.bot.queue[ctx.guild.id][0]['id']}", options=ffmpeg_options)

            try:
                ctx.guild.voice_client.play(
                    discord.PCMVolumeTransformer(
                        src, 
                        volume=vol
                    )
                )
            except Exception as exc:
                self.bot.logger.warning(f"ERROR: {exc}")
                self.bot.queue[ctx.guild.id].pop(0)
            else:
                try:
                    while ctx.guild.voice_client.is_playing() or ctx.guild.voice_client.is_paused():
                        await asyncio.sleep(1)
                        vol = ctx.voice_client.source.volume
                except AttributeError:
                    pass

                if self.bot.loop_queue[ctx.guild.id]:
                    self.bot.queue[ctx.guild.id].append(self.bot.queue[ctx.guild.id][0])
                self.bot.queue[ctx.guild.id].pop(0)

async def setup(bot):
    await bot.add_cog(mido_music(bot))

    if not hasattr(bot, "queue"):
        bot.queue = dict()
    if not hasattr(bot, "loop_queue"):
        bot.loop_queue = dict()
