import discord

class Confirm(discord.ui.View):

    def __init__(
        self, *, msg_y: str=None, msg_n: str=None, msg=None
    ):
        super().__init__()

        self._confirmed = None
        self.msg_yes = msg_y if msg_y else "Confirming！"
        self.msg_no = msg_n if msg_n else "Cancelling！"
        self.msg = msg

    #confirm button
    @discord.ui.button(
        label="confirm",
        style=discord.ButtonStyle.green
    )
    async def confirm(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message(
            self.msg_yes,
            ephemeral=True
        )
        self._confirmed = True
        self.stop()

    #cancelled
    @discord.ui.button(
        label="cancel",
        style=discord.ButtonStyle.red
    )
    async def cancel(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message(
            self.msg_no,
            ephemeral=True
        )
        self._confirmed = False
        self.stop()
