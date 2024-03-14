import disnake, sqlite3, asyncio

from disnake.ext import commands

from ssbot import SSBot, BOT
from cogs.hadlers import utils
from cogs.systems.rate_system.stars_button import StarsButton
from cogs.view.buttons.enter_description_button import EnterDescriptionButton


class SendReviewButtonReg(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("SendReviewButton was added")
        self.client.add_view(SendReviewButton(bot=self.client))


class SendReviewButton(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Отправить отзыв", style=disnake.ButtonStyle.blurple, custom_id="send_review_button")
    async def send_review(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        REVIEWS_CHANNEL = BOT.get_channel(BOT.BOT_CONFIG["feedback_channel_id"])
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

        review = disnake.Embed(title=f"Отзыв:", color=SSBot.DEFAULT_COLOR)
        review.add_field(name=f"Оценка: {await utils.star_count_conv(count=var_stars)}", value=var_description, inline=False)
        review.set_author(name=interaction.author.display_name, icon_url=avatar)
        try:
            image = await utils.get_files(f"cache/{interaction.author.name}/")
            file = disnake.File(image[0], filename="review_image_for_send.jpg")
            review.set_image(url="attachment://review_image_for_send.jpg")
        except:
            pass

        await REVIEWS_CHANNEL.send(embed=review, file=file)
        await interaction.send("Данная ветка удалится через 20 секунд.")

        try:
            await utils.delete_files_from_cache(interaction.author.name)
        except FileNotFoundError:
            pass

        await asyncio.sleep(20)

        await interaction.channel.delete()


def setup(client):
    client.add_cog(SendReviewButtonReg(client))
