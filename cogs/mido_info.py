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
            e.add_field(name="Country", value=req["country"])
            e.add_field(name="City", value=req["city"])
            e.add_field(name="Region", value=req["region"])
            v = f"""ASN: {req['asn']['asn']}
            ASN Name: {req['asn']['name']}
            ASN Domain: {req['asn']['domain']}
            ASN Route: {str(req['asn']['route'])}
            ASN Type: {req['asn']['type']}
            """
            e.add_field(name="ASN", value=v, inline=False)
            v = f"""Name: {req['company']['name']}
            Domain: {req['company']['domain']}
            Type: {req['company']['type']}
            """
            e.add_field(name="Company", value=v, inline=False)
            v = f"""VPN: {'Yes' if req['privacy']['vpn'] else 'No'}
            Proxy: {'Yes' if req['privacy']['proxy'] else 'No'}
            Tor: {'Yes' if req['privacy']['tor'] else 'No'}
            Relay: {'Yes' if req['privacy']['relay'] else 'No'}
            Hosting: {'Yes' if req['privacy']['hosting'] else 'No'}
            Service: {req['privacy']['service'] if req['privacy']['service'] else 'Unknown'}
            """
            e.add_field(name="Privacy", value=v, inline=False)
            v = f"""Address: {req['abuse']['address']}
            Country: {req['abuse']['country']}
            Email: {req['abuse']['email']}
            Name: {req['abuse']['name']}
            Network: {str(req['abuse']['network'])}
            Phone: {str(req['abuse']['phone'])}
            """
            e.add_field(name="Abuse", value=v, inline=False)
            return await msg.edit(content=None, embed=e)

async def setup(bot):
    await bot.add_cog(mido_info(bot))
