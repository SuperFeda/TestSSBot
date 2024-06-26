import disnake

from disnake.ext import commands

from main import SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds.ordering_embeds import CHECKING_ORDER_EMBED
from cogs.view.buttons.donation_and_promo_code_buttons import DonationAndPromoCodeButtons
from cogs.view.modals_menu.additional_contacts import AdditionalContactsMenu


class ContinueAndAdtConButtonsReg(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ContinueAndAdtConButtons was added")
        self.bot.add_view(ContinueAndAdtConButtons(bot=self.bot))


class ContinueAndAdtConButtons(disnake.ui.View):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.green, custom_id="continue_button")
    async def continue_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        user_id: int = interaction.author.id

        # find client name
        SSBot.CLIENT_DB_CURSOR.execute("SELECT client_name FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_client_name = result[0] if result else None

        # find client display name
        SSBot.CLIENT_DB_CURSOR.execute("SELECT client_display_name FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_client_display_name = result[0] if result else None

        # find service type
        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_type FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_service_type = result[0] if result else None

        # find service description
        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_description FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_service_description = result[0] if result else None

        # find service code
        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_code FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_service_code = result[0] if result else None

        # find sending time
        SSBot.CLIENT_DB_CURSOR.execute("SELECT sending_time FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_sending_time = result[0] if result else None

        # find vk
        SSBot.CLIENT_DB_CURSOR.execute("SELECT vk_url FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_vk_url = result[0] if result else None

        # find mail
        SSBot.CLIENT_DB_CURSOR.execute("SELECT mail FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_mail = result[0] if result else None

        # find telegram url
        SSBot.CLIENT_DB_CURSOR.execute("SELECT telegram_url FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_telegram_url = result[0] if result else None

        color: disnake.Color = await utils.color_order(var_service_type)  # получение цвета для embed

        order_embed: disnake.Embed = disnake.Embed(title='Ваш заказ:', color=color)
        order_embed.add_field(name=f'Код заказа: {var_service_code}\nДата оформления: {var_sending_time} (МСК / GMT+3)\nИмя заказчика: {var_client_display_name} (tag: {var_client_name})\nУслуга: {await utils.convert_value_to_service_name(var_service_type)}', value="")
        order_embed.add_field(name="Описание:", value=var_service_description, inline=False)

        if var_mail != "" and var_mail is not None or var_vk_url != "" and var_vk_url is not None or var_telegram_url != "" and var_telegram_url is not None:
            order_embed.add_field(name="Доп. контакты связи:", value="", inline=False)
            if var_vk_url != "" and var_vk_url is not None:
                order_embed.add_field(name=f'VK: {var_vk_url}', value="", inline=False)
            if var_mail != "" and var_mail is not None:
                order_embed.add_field(name=f'Электронная почта: {var_mail}', value="", inline=False)
            if var_telegram_url != "" and var_telegram_url is not None:
                order_embed.add_field(name=f'Telegram: {var_telegram_url}', value="", inline=False)

        avatar = await utils.get_avatar(interaction.author.avatar)
        order_embed.set_author(name=var_client_display_name, icon_url=avatar)

        try:
            pictures: list = await utils.get_files_disnake(f"cache/{interaction.author.name}/")
            await interaction.response.send_message(embeds=[CHECKING_ORDER_EMBED, order_embed], files=pictures, view=DonationAndPromoCodeButtons(self.bot))
        except FileNotFoundError:
            await interaction.response.send_message(embeds=[CHECKING_ORDER_EMBED, order_embed], view=DonationAndPromoCodeButtons(self.bot))

    @disnake.ui.button(label="Доп. контакты", style=disnake.ButtonStyle.blurple, custom_id="additional_contacts_button")
    async def additional_contacts_button(self, button: disnake.ui.Button, ctx: disnake.AppCmdInter):
        await ctx.response.send_modal(modal=AdditionalContactsMenu(self.bot))

    def to_components(self):
        return super().to_components()


def setup(bot):
    bot.add_cog(ContinueAndAdtConButtonsReg(bot))
