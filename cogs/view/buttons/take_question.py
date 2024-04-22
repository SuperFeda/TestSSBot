import disnake

from disnake.ext import commands

from main import SSBot, BOT
from cogs.hadlers import utils


class TakeQuestionButtonReg(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("TakeQuestionButton was added")
        self.bot.add_view(TakeQuestionButton(bot=self.bot))


class TakeQuestionButton(disnake.ui.View):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Принять", style=disnake.ButtonStyle.green, custom_id="take_question_button")
    async def take_question(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        SUPPORT_CHANNEL: disnake.TextChannel = BOT.get_channel(SSBot.BOT_DATA["support_channel_id"])
        message: disnake.Message = await interaction.channel.fetch_message(interaction.message.id)
        client_id_from_embed: str = message.embeds[0]._fields[1]["value"]
        client: disnake.Member = interaction.guild.get_member(int(client_id_from_embed))
        avatar: disnake.Member.avatar = await utils.get_avatar(ctx_user_avatar=interaction.author.avatar)

        embed = message.embeds[0]
        embed.set_footer(
            text=f"Вопрос принял {interaction.author.display_name}",
            icon_url=avatar
        )
        await message.edit(embed=embed, view=None)

        thread: disnake.Thread = await SUPPORT_CHANNEL.create_thread(
            name=f"Диалог с {client.display_name}",
            type=disnake.ChannelType.private_thread
        )

        await thread.send(f"<@{interaction.author.id}> <@{client.id}>")


def setup(client):
    client.add_cog(TakeQuestionButtonReg(client))
