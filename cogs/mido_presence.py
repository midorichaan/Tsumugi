import discord
from discord.ext import commands

import datetime

class mido_presence(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._fired = {}

    #on_presence_update
    @commands.Cog.listener()
    async def on_presence_update(self, bef, af):
        if not af.activity:
            if self._fired.get(af.id, None):
                del self._fired[af.id]
            return
        if af.id in self.bot.instance["ids"]:
            self._fired[af.id] = 1
            self._fired[af.id] += 1
            channel = self.bot.get_channel(self.bot.instance["channels"]["presence"])
            e = discord.Embed(
                description=f"__**{af.activity.name}**__ をプレイ中",
                color=0xf996ff,
                timestamp=datetime.datetime.now()
            )
            e.set_author(name=f"{af} ({af.id})", icon_url=af.avatar.replace(static_format="png"))
            if self._fired[af.id] == 3:
                await channel.send(embed=e)

async def setup(bot):
    if not bot.instance.get("channels", None):
        bot.instance["channels"] = {
            "presence": 958344128092074055
        }
    if not bot.instance.get("ids", None):
        bot.instance["ids"] = []

    await bot.add_cog(mido_presence(bot))
