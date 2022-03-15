import discord
from discord.ext import commands

class Button(discord.ui.View):

    def __init__(self):
        super().__init__()

    @discord.ui.button(
        label="A",
        style=discord.ButtonStyle.primary,
    )
    async def _A(self, button, interact):
        await interact.response.send_message(
            "A",
            ephemeral=True
        )
        self.stop()

    @discord.ui.button(
        label="B",
        style=discord.ButtonStyle.secondary
    )
    async def _B(self, button, interact):
        await interact.response.send_message(
            "B",
            ephemeral=True
        )
        self.stop()

    @discord.ui.button(
        label="C",
        style=discord.ButtonStyle.success,
    )
    async def _C(self, button, interact):
        await interact.response.send_message(
            "C",
            ephemeral=True
        )
        self.stop()

    @discord.ui.button(
        label="D",
        style=discord.ButtonStyle.danger,
    )
    async def _D(self, button, interact):
        await interact.response.send_message(
            "D",
            ephemeral=True
        )
        self.stop()

    @discord.ui.button(
        label="E",
        style=discord.ButtonStyle.link,
        #url="https://twitter.com/Midorichaan2525"
    )
    async def _C(self, button, interact):
        pass

class mido_test(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #button
    @commands.command(
        name="button",
        description="ボタンのテストコマンド"
    )
    async def _button(self, ctx):
        await ctx.send("View test", view=Button())

async def setup(bot):
    await bot.add_cog(mido_test(bot))
