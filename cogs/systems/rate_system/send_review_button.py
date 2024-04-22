import disnake

from disnake.ext import commands
from asyncio import sleep

from main import SSBot, BOT
from cogs.hadlers import utils


class SendReviewButtonReg(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("SendReviewButton was added")
        self.bot.add_view(SendReviewButton(bot=self.bot))


class SendReviewButton(disnake.ui.View):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Отправить отзыв", style=disnake.ButtonStyle.blurple, custom_id="send_review_button")
    async def send_review(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        REVIEWS_CHANNEL: disnake.TextChannel = BOT.get_channel(BOT.BOT_CONFIG["feedback_channel_id"])
        avatar: disnake.Member.avatar = await utils.get_avatar(interaction.author.avatar)
        user_id: int = interaction.author.id
        file = None

        SSBot.CLIENT_DB_CURSOR.execute("SELECT stars FROM settings WHERE user_id=?", (user_id,))
        result_ = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_stars = result_[0] if result_ else None

        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_description FROM settings WHERE user_id=?", (user_id,))
        result_ = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_description = result_[0] if result_ else None

        review: disnake.Embed = disnake.Embed(title=f"Отзыв:", color=SSBot.DEFAULT_COLOR)
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

        await sleep(20)

        await interaction.channel.delete()


def setup(bot):
    bot.add_cog(SendReviewButtonReg(bot))
