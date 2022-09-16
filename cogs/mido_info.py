import discord
from discord.ext import commands

from lib import utils

class mido_info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #ipinfo
    @commands.command(name="ipinfo", description="IPアドレスの情報を表示します", usage="ipinfo <ip>")
    async def _ipinfo(self, ctx, ipaddr: str=None):
        msg = await utils.reply_or_send(ctx, content=f"> 処理中...")

        if not ipaddr:
            return await msg.edit(content="> IPアドレスを入力してね！")

        try:
            req = await self.bot.ipinfo.get_data(ipaddr)
        except Exception as exc:
            return await msg.edit(content=f"> エラー \n```py\n{exc}\n```")
        else:
            e = discord.Embed(title=f"IP Info: {ipaddr}", timestamp=ctx.message.created_at)
            e.add_field(name="HostName", value=req["hostname"])
            e.add_field(name="AnyCast", value="Yes" if req["anycast"] else "No")
            e.add_field(name="City", value=req["city"])
            e.add_field(name="Region", value=req["region"])
            e.add_field(name="Country", value=req["country"])
            e.add_field(name="Location", value=req["loc"])
            return await msg.edit(content=None, embed=e)

async def setup(bot):
    await bot.add_cog(mido_info(bot))
