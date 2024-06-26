import disnake

from disnake.ext.commands import Cog, Bot

from main import SSBot, BOT
from cogs.view.buttons.take_question import TakeQuestionButton
from cogs.hadlers.embeds.template_embeds import NOTIFICATION_SEND_EMBED


class ContactHereButtonReg(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("TakeQuestionButton was added")
        self.bot.add_view(ContactHereButton(bot=self.bot))


class ContactHereButton(disnake.ui.View):

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Связаться здесь", style=disnake.ButtonStyle.blurple, custom_id="contact_here_button")
    async def contact_here(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        QUESTIONS_CHANNEL = BOT.get_channel(SSBot.BOT_DATA["questions_channel_id"])

        embed_for_qs: disnake.Embed = disnake.Embed(title="Новый вопрос", color=disnake.Color.blurple())
        embed_for_qs.add_field(name=f"Имя: {interaction.author.display_name} ({interaction.author.name})", value="", inline=False)
        embed_for_qs.add_field(name="ID:", value=interaction.author.id, inline=False)

        await QUESTIONS_CHANNEL.send(embed=embed_for_qs, view=TakeQuestionButton(self.bot))
        await interaction.send(embed=NOTIFICATION_SEND_EMBED, ephemeral=True)


def setup(client):
    client.add_cog(ContactHereButtonReg(client))
