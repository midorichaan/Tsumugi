import discord
from discord import app_commands
from discord.ext import commands

import asyncio
import datetime
import functools
import os
import random
import youtube_dl

from apiclient.discovery import build
from dotenv import load_dotenv
from lib import utils as util, paginator

#load .env file
load_dotenv()

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "musics/%(id)s",
    "restrictfilenames": True,
    "nocheckcertificate": True,
    "noplaylist": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    'geo-bypass': True,
    'verbose': False
}

ffmpeg_options = {
    'before_options': '-loglevel fatal -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

class mido_music_slash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
       # self.youtube = build("youtube", "v3", developerKey=os.environ["YOUTUBE_KEY"])

    #get_data
    async def get_data(
        self, 
        key: str, 
        download: bool=False
    ):
        loop = self.bot.loop or asyncio.get_event_loop()

        try:
            data = await loop.run_in_executor(None, functools.partial(self.ytdl.extract_info, key, download=download))
        except Exception as exc:
            raise exc

        return data

    #get_info
    async def get_info(
        self, 
        interact: discord.Interaction, 
        url: str, 
        download: bool=True
    ):
        data = await self.get_data(url, download)

        result = {
            "type": "Download" if download else "Stream",
            "url": data.get("url", "unknown"),
            "id": data.get("id", "unknown"),
            "webpage_url": data.get("webpage_url", "unknown"),
            "title": data.get("title", "unknown"),
            "thumbnail": data.get("thumbnail", "unknown"),
            "uploader": data.get("uploader", "unknown"),
            "uploader_url": data.get("uploader_url", "unknown"),
            "request": interact.user.id
        }

        return result

    #_play
    async def _play(
        self, 
        interact: discord.Interaction, 
        vol: float=0.5, 
        src=None
    ):
        if not self.bot.loop_queue.get(interact.guild.id, None):
            self.bot.loop_queue[interact.guild.id] = False

        while self.bot.queue.get(interact.guild.id, None):
            if self.bot.queue[interact.guild.id][0]["type"] == "Stream":
                src = discord.FFmpegPCMAudio(
                    self.bot.queue[interact.guild.id][0]["url"], 
                    options=ffmpeg_options
                )
            elif self.bot.queue[interact.guild.id][0]["type"] == "Download":
                src = discord.FFmpegPCMAudio(
                    f"musics/{self.bot.queue[interact.guild.id][0]['id']}", 
                    options=ffmpeg_options
                )

            try:
                interact.guild.voice_client.play(
                    discord.PCMVolumeTransformer(
                        src,
                        volume=vol
                    )
                )
            except Exception as exc:
                self.bot.logger.warning(f"ERROR: {exc}")
                self.bot.queue[interact.guild.id].pop(0)
            else:
                try:
                    while interact.guild.voice_client.is_playing() or interact.guild.voice_client.is_paused():
                        await asyncio.sleep(1)
                        vol = interact.guild.voice_client.source.volume
                except AttributeError:
                    pass

                if self.bot.loop_queue[interact.guild.id]:
                    self.bot.queue[interact.guild.id].append(self.bot.queue[interact.guild.id][0])
                self.bot.queue[interact.guild.id].pop(0)

    #group command
    group = app_commands.Group(
        name="music",
        description="音楽機能",
        guild_only=True,
    )

    #shuffle
    @group.command(name="shuffle", description="キューをシャッフルします。")
    async def _shuffle(self, interact: discord.Interaction):
        if interact.user.voice:
            if interact.guild.voice_client:
                if interact.user.voice.channel == interact.guild.voice_client.channel:
                    if self.bot.queue.get(interact.guild.id, None):
                        for i in range(5):
                            random.shuffle(self.bot.queue[interact.guild.id])
                        return await interact.response.send_message(
                            content="> キューをシャッフルしたよ！"
                        )
                    else:
                        return await interact.response.send_message(
                            content="> キューが存在しないよ！"
                        )
                else:
                    return await interact.response.send_message(
                        content="> Botと同じチャンネルに接続する必要があるよ！"
                    )
            else:
                return await interact.response.send_message(
                    content="> Botがボイスチャンネルに接続していないよ！"
                )
        else:
            return await interact.response.send_message(
                content="> ボイスチャンネルに接続してね！"
            )

    #stop
    @group.command(name="stop", description="音楽の再生を停止し、キューを削除してボイスチャンネルから退出します。")
    async def _stop(self, interact: discord.Interaction):
        if interact.user.voice:
            if interact.guild.voice_client:
                if interact.user.voice.channel == interact.guild.voice_client.channel:
                    try:
                        await interact.guild.voice_client.disconnect()

                        try:
                            del self.bot.queue[interact.guild.id]
                            del self.bot.loop_queue[interact.guild.id]
                        except:
                            pass
                    except Exception as exc:
                        return await interact.response.send_message(
                            content=f"> エラー \n```\n{exc}\n```"
                        )
                    else:
                        return await interact.response.send_message(
                            content=f"> 再生を停止し、ボイスチャンネルから退出しました！"
                        )
                else:
                    return await interact.response.send_message(
                        content=f"> Botと同じチャンネルに接続する必要があるよ！"
                    )
            else:
                return await interact.response.send_message(
                    content=f"> ボイスチャンネルに接続いないから使えないよ！"
                )
        else:
            return await interact.response.send_message(
                content=f"> ボイスチャンネルに接続してね！"
            )

    #play
    @group.command(name="play", description="音楽を再生します。")
    @app_commands.describe(query="検索するURL・内容")
    async def _music_play(self, interact: discord.Interaction, query: str=None):
        await interact.response.defer()

        if interact.user.voice:
            if not interact.guild.voice_client:
                try:
                    vc = await interact.user.voice.channel.connect()
                except Exception as exc:
                    return await interact.followup.send(
                        content=f"> エラー \n```\n{exc}\n```"
                    )
        else:
            return await interact.followup.send(
                content=f"> ボイスチャンネルに接続してね！"
            )

        if interact.guild.voice_client.is_paused():
            interact.guild.voice_client.resume()
            return await interact.followup.send(
                content="> 再生を再開したよ！"
            )
            
        msg = await interact.followup.send(content="> 処理中...", wait=True)

        if not query:
            await msg.edit(content="> 検索ワード/URLを送信してください。")

            try:
                message = await self.bot.wait_for("message", check=lambda m: m.author.id == interact.user.id and m.channel.id == interact.channel.id, timeout=30.0)
            except asyncio.TimeoutError:
                return await msg.edit(
                    content="> 30秒が経過したからキャンセルされたよ！"
                )
            else:
                await msg.edit(
                    content="> 再生処理を行っています...."
                )
                query = message.content

        if not query.startswith("stream:"):
            try:
                data = await self.get_data(query[9:], True)
            except Exception as exc:
                return await msg.edit(
                    content=f"> エラー \n```\n{exc}\n```"
                )
            else:
                if not data:
                    return await msg.edit(
                        content="> 動画の処理中にエラーが発生しました"
                    )

                if data.get("_type", None) == "playlist":
                    try:
                        d = await self.get_info(interact, f"https://youtu.be/{data['entries'][0]['id']}", True)
                    except Exception as exc:
                        return await msg.edit(
                            content=f"> エラー \n```py\n{exc}\n```"
                        )
                    else:
                        if self.bot.queue.get(interact.guild.id, None):
                            self.bot.queue[interact.guild.id] = self.bot.queue[interact.guild.id] + [d]
                            return await msg.edit(
                                content=f"> キューに{d['title']}を追加したよ！"
                            )
                        else:
                            self.bot.queue[interact.guild.id] = [d]
                            await msg.edit(
                                content=f"> {d['title']}を再生するよ！"
                            )
                            self.bot.loop.create_task(self._play(interact))
                else:
                    d = await self.get_info(interact, f"https://youtu.be/{data['id']}", True)
                    if self.bot.queue.get(interact.guild.id, None):
                        self.bot.queue[interact.guild.id] = self.bot.queue[interact.guild.id] + [d]
                        return await msg.edit(
                            content=f"> キューに{ret['title']}を追加したよ！"
                        )
                    else:
                        self.bot.queue[interact.guild.id] = [d]
                        await msg.edit(
                            content=f"> {d['title']}を再生するよ！"
                        )
                        self.bot.loop.create_task(self._play(interact))
        else:
            try:
                data = await self.get_data(query, False)
            except Exception as exc:
                return await msg.edit(
                    content=f"> エラー \n```\n{exc}\n```"
                )
            else: 
                if not data:
                    return await msg.edit(
                        content="> 動画の処理中にエラーが発生しました"
                    )
                lists = []

                #from sina () maybe only youtube
                if data.get("_type", None) == "playlist":
                    if len(data["entries"]) >= 5:
                        lists.append(self.get_info(interact, f"https://www.youtube.com/watch?v={data['entries'][0]['id']}", False))
                    else:    
                        for i in data["entries"]:
                            lists.append(self.get_info(interact, f"https://www.youtube.com/watch?v={i['id']}", False))

                    try:
                        ret = [r for r in await asyncio.gather(*lists) if r]
                    except Exception as exc:
                        return await msg.edit(
                            content=f"> エラー \n```\n{exc}\n```"
                        )
                    else:
                        if not ret:
                            return await msg.edit(
                                content="> 再生処理中にエラーが発生しました"
                            )

                    if self.bot.queue.get(interact.guild.id, None):
                        self.bot.queue[interact.guild.id] = self.bot.queue[interact.guild.id] + ret
                        return await msg.edit(
                            content=f"> キューに{len(ret)}本の動画を追加したよ！"
                        )
                    else:
                        self.bot.queue[interact.guild.id] = ret
                        await msg.edit(
                            content=f"> プレイリストからの{len(ret)}本の動画を再生するよ！"
                        )
                        self.bot.loop.create_task(self._play(interact))
                else:
                    ret = await self.get_info(interact, f"https://www.youtube.com/watch?v={data['id']}", False)

                    if self.bot.queue.get(interact.guild.id, None):
                        self.bot.queue[interact.guild.id] = self.bot.queue[interact.guild.id] + [ret]
                        return await msg.edit(
                            content=f"> キューに{ret['title']}を追加したよ！"
                        )
                    else:
                        self.bot.queue[interact.guild.id] = [ret]
                        await msg.edit(
                            content=f"> {ret['title']}を再生するよ！"
                        )
                        self.bot.loop.create_task(self._play(interact))

    #skip
    @group.command(name="skip", description="曲をスキップします。")
    async def _skip(self, interact: discord.Interaction):
        if interact.user.voice:
            if interact.guild.voice_client:
                if not interact.guild.voice_client.channel == interact.user.voice.channel:
                    return await interact.response.send_message(
                        content="> Botと同じチャンネルに接続している必要があるよ！"
                    )

                if interact.guild.voice_client.is_playing():
                    loop = self.bot.loop_queue[interact.guild.id]
                    self.bot.loop_queue[interact.guild.id] = False
                    interact.guild.voice_client.stop()
                    self.bot.loop_queue[interact.guild.id] = loop
                    return await interact.response.send_message(
                        content="> 曲をスキップしたよ！"
                    )
                else:
                    return await interact.response.send_message(
                        content=f"> 再生中のみスキップできるよ！"
                    )
            else:
                return await interact.response.send_message(
                    content="> このサーバーでは何も再生していないよ！"
                )
        else:
            return await interact.response.send_message(
                content=f"> ボイスチャンネルに接続してね！"
            )

    #pause
    @group.command(name="pause", description="曲の再生を一時停止します。")
    async def _pause(self, interact: discord.Interaction):
        if interact.user.voice:
            if interact.guild.voice_client:
                if not interact.guild.voice_client.channel == interact.author.voice.channel:
                    return await interact.response.send_message(
                        content="> Botと同じチャンネルに接続している必要があるよ！"
                    )

                if interact.guild.voice_client.is_playing():
                    interact.guild.voice_client.pause()
                    return await interact.response.send_message(
                        content="> 曲を一時停止したよ！"
                    )
                else:
                    return await interact.response.send_message(
                        content=f"> 再生中のみ一時停止できるよ！"
                    )
            else:
                return await interact.response.send_message(
                    content="> このサーバーでは何も再生していないよ！"
                )
        else:
            return await interact.response.send_message(
                content=f"> ボイスチャンネルに接続してね！"
            )

    #volume
    @group.command(name="volume", description="音量を変更します。")
    @app_commands.describe(vol="音楽の音量")
    async def _volume(self, interact: discord.Interaction, vol: float=None):
        if interact.user.voice:
            if interact.guild.voice_client:
                if not interact.guild.voice_client.channel == interact.user.voice.channel:
                    return await interact.response.send_message(
                        content="> 私と同じチャンネルに接続している必要があるよ！"
                    )

                if not interact.guild.voice_client.is_playing():
                    return await interact.response.send_message(
                        content="> 再生中のみ変更できるよ！"
                    )

                if not vol:
                    return await interact.response.send_message(
                        content="> 音量を指定してね！"
                    )

                interact.guild.voice_client.source.volume = vol / 100.0
                return await interact.response.send_message(
                    content=f"> 音量を{vol}にしたよ！！"
                )
            else:
                return await interact.response.send_message(
                    content="> このサーバーでは何も再生していないよ！"
                )
        else:
            return await interact.response.send_message(
                content=f"> ボイスチャンネルに接続してね！"
            )

    #nowplaying
    @group.command(name="nowplaying", description="現在再生中の音楽を表示します。")
    async def _nowplaying(self, interact: discord.Interaction):
        if interact.guild.voice_client:
            if interact.guild.voice_client.is_playing():
                queue = self.bot.queue[interact.guild.id][0]

                e = discord.Embed(title="🎶Now Playing", color=self.bot.color, timestamp=interact.message.created_at)
                e.set_thumbnail(url=queue["thumbnail"])
                e.set_footer(text=f"Requested by {self.bot.get_user(queue['request'])}", icon_url=self.bot.get_user(queue["request"]).avatar)
                e.add_field(name="再生中の曲", value=f"[{queue['title']}]({queue['webpage_url']})")
                e.add_field(name="アップロードチャンネル", value=f"[{queue['uploader']}]({queue['uploader_url']})")
                return await interact.response.send_message(
                    embed=e
                )
            else:
                return await interact.response.send_message(
                    content="> 現在再生中の曲はないよ！"
                )
        else:
            return await interact.response.send_message(
                content="> このサーバーでは何も再生していないよ！"
            )

    #queue
    @group.command(name="queue", description="キューを表示します。")
    async def _queue(self, interact: discord.Interaction):
        if not interact.guild.voice_client:
            return await interact.response.send_message(
                content="> このサーバーでは何も再生していないよ！"
            )

        if self.bot.queue.get(interact.guild.id, []) == []:
            return await interact.response.send_message(
                content="> キューに何も追加されてないよ！"
            )

        e = discord.Embed(title="🎶Music Queues", description="", color=self.bot.color, timestamp=datetime.datetime.now())
        count = 1
        for i in self.bot.queue[interact.guild.id]:
            e.description += f"{count}. [{i['title']}]({i['webpage_url']})\n"
            count += 1
        return await interact.response.send_message(
            embed=e
        )

    #loop
    @group.command(name="loop", description="曲のループを切り替えます。")
    async def _loop(self, interact: discord.Interaction, loop: bool=None):
        if interact.user.voice:
            if interact.guild.voice_client:
                if not interact.guild.voice_client.channel == interact.user.voice.channel:
                    return await interact.response.send_message(
                        content="> Botと同じチャンネルに接続している必要があるよ！"
                    )

                if not interact.guild.voice_client.is_playing():
                    return await interact.response.send_message(
                        content="> 再生中のみ変更できるよ！"
                    )

                if loop:
                    self.bot.loop_queue[interact.guild.id] = loop
                    return await interact.response.send_message(
                        content=f"> ループを{loop}にしたよ！"
                    )
                else:
                    if self.bot.loop_queue[interact.guild.id]:
                        self.bot.loop_queue[interact.guild.id] = False
                        return await interact.response.send_message(
                            content=f"> ループをFalseにしたよ！"
                        )
                    else:
                        self.bot.loop_queue[interact.guild.id] = True
                        return await interact.response.send_message(
                            content=f"> ループをTrueにしたよ！"
                        )
            else:
                return await interact.response.send_message(
                    content="> このサーバーでは何も再生していないよ！"
                )
        else:
            return await interact.response.send_message(
                content=f"> ボイスチャンネルに接続してね！"
            )

    #delete
    @group.command(name="delete", description="キューから曲を削除します。")
    @app_commands.describe(index="キューの番号。")
    async def _delete(self, interact: discord.Interaction, index: int=None):
        if not index:
            return await interact.response.send_message(
                content="> 削除する曲の番号を入力してね！"
            )

        if index <= 0:
            return await interact.response.send_message(
                content="> 1以上の値を指定してね！"
            )

        if interact.user.voice:
            if interact.guild.voice_client:
                if not interact.guild.voice_client.channel == interact.user.voice.channel:
                    return await interact.response.send_message(
                        content="> Botと同じチャンネルに接続している必要があるよ！"
                    )

                q = self.bot.queue.get(interact.guild.id, None)
                if q is not None:
                    index = index - 1

                    if len(q) <= index:
                        return await interact.response.send_message(
                            content="> その値は指定できないよ！"
                        )

                    try:
                        del q[index]
                        return await interact.response.send_message(
                            content=f"> {index + 1}番目の曲を削除したよ！"
                        )
                    except Exception as exc:
                        return await interact.response.send_message(
                            content=f"> エラー \n```py\n{exc}\n```"
                        )
                else:
                    return await interact.response.send_message(
                        content="> キューが存在しないよ！"
                    )
            else:
                return await interact.response.send_message(
                    content="> このサーバーでは何も再生していないよ！"
                )
        else:
            return await interact.response.send_message(
                content=f"> ボイスチャンネルに接続してね！"
            )

async def setup(bot):
    await bot.add_cog(mido_music_slash(bot))

    if not hasattr(bot, "queue"):
        bot.queue = dict()
    if not hasattr(bot, "loop_queue"):
        bot.loop_queue = dict()
