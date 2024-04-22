import disnake

from disnake.ext.commands import Cog, Bot

from main import SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds.template_embeds import REVIEW_CHECKING_EMBED
from cogs.systems.rate_system.send_review_button import SendReviewButton


class ContinueButtonForReviewReg(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("ContinueButtonForReview was added")
        self.bot.add_view(ContinueButtonForReview(bot=self.bot))


class ContinueButtonForReview(disnake.ui.View):

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.green, custom_id="continue_button_for_review")
    async def continue_button_for_review(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        avatar: disnake.Member.avatar = await utils.get_avatar(interaction.author.avatar)
        user_id: int = interaction.author.id
        file = None

        SSBot.CLIENT_DB_CURSOR.execute("SELECT stars FROM settings WHERE user_id=?", (user_id,))
        result_ = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_stars = result_[0] if result_ else None

        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_description FROM settings WHERE user_id=?", (user_id,))
        result_ = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_description = result_[0] if result_ else None

        review = disnake.Embed(title="Ваш отзыв:", color=SSBot.DEFAULT_COLOR)
        review.add_field(name=f"Оценка: {await utils.star_count_conv(count=var_stars)}", value=var_description, inline=False)
        review.set_author(name=interaction.author.display_name, icon_url=avatar)
        try:
            image = await utils.get_files(f"cache/{interaction.author.name}/")
            file = disnake.File(image[0], filename="review_image_for_send.jpg")
            review.set_image(url="attachment://review_image_for_send.jpg")
        except:
            pass

        if file is not None:
            await interaction.send(embeds=[REVIEW_CHECKING_EMBED, review], file=file, view=SendReviewButton(self.bot))
        else:
            await interaction.send(embeds=[REVIEW_CHECKING_EMBED, review], view=SendReviewButton(self.bot))


def setup(client):
    client.add_cog(ContinueButtonForReviewReg(client))
