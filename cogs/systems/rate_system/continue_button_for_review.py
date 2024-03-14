import disnake, sqlite3

from disnake.ext import commands

from ssbot import SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds.template_embeds import REVIEW_CHECKING_EMBED
from cogs.systems.rate_system.send_review_button import SendReviewButton


class ContinueButtonForReviewReg(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("ContinueButtonForReview was added")
        self.client.add_view(ContinueButtonForReview(bot=self.client))


class ContinueButtonForReview(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.green, custom_id="continue_button_for_review")
    async def continue_button_for_review(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        avatar = await utils.get_avatar(interaction.author.avatar)
        user_id = interaction.author.id
        file = None

        connection_ = sqlite3.connect(SSBot.PATH_TO_CLIENT_DB)
        cursor_ = connection_.cursor()

        cursor_.execute("SELECT stars FROM settings WHERE user_id=?", (user_id,))
        result_ = cursor_.fetchone()
        var_stars = result_[0] if result_ else None

        cursor_.execute("SELECT service_description FROM settings WHERE user_id=?", (user_id,))
        result_ = cursor_.fetchone()
        var_description = result_[0] if result_ else None

        connection_.close()

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
