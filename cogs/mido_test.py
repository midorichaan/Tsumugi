import discord
from discord.ext import commands

class Modal(discord.ui.Modal):
    name = discord.ui.TextInput(label="Username", style=discord.TextStyle.paragraph)
    id = discord.ui.TextInput(label="ID", style=discord.TextStyle.short)

    def __init__(self):
        super().__init__()
        self.title = "Test Modal"

    async def on_submit(self, interact):
        await interact.response.send_message(
            f"> Modal Submitted \n{name}, {id}"
        )

class Button(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="E",
                url="https://twitter.com/Midorichaan2525"
            )
        )

    @discord.ui.button(
        label="A",
        style=discord.ButtonStyle.primary,
    )
    async def _A(self, button, interact):
        await interact.response.send_message(
            "A",
            ephemeral=True
        )

    @discord.ui.button(
        label="B",
        style=discord.ButtonStyle.secondary
    )
    async def _B(self, button, interact):
        await interact.response.send_message(
            "B",
            ephemeral=True
        )

    @discord.ui.button(
        label="C",
        style=discord.ButtonStyle.success,
    )
    async def _C(self, button, interact):
        await interact.response.send_message(
            "C",
            ephemeral=True
        )

    @discord.ui.button(
        label="D",
        style=discord.ButtonStyle.danger,
    )
    async def _D(self, button, interact):
        await interact.response.send_message(
            "D",
            ephemeral=True
        )

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

    #modal
    @commands.command(
        name="modal",
        description="Modalのテストコマンド"
    )
    async def _modal(self, ctx):
        modal = Modal()
        await modal.wait()

async def setup(bot):
    await bot.add_cog(mido_test(bot))
