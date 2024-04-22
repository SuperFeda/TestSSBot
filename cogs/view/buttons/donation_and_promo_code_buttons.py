from disnake import ButtonStyle, Embed, Color, AppCmdInter, MessageInteraction, TextChannel, Member
from disnake.ui import View
from disnake.ui.button import button, Button
from disnake.ext.commands import Cog, Bot

from main import SSBot, BOT
from cogs.hadlers import utils, dicts
from cogs.view.buttons.take_order import TakeOrder
from cogs.view.modals_menu.promo_code_enter import PromoCodeEnterMenu


class DonationAndPromoCodeButtonsReg(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("DonationAndPromoCodeButtons was added")
        self.bot.add_view(DonationAndPromoCodeButtons(bot=self.bot))


class DonationAndPromoCodeButtons(View):

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @button(label="Оплатить", style=ButtonStyle.blurple, custom_id="pay_button")
    async def pay_button(self, button_: Button, ctx: MessageInteraction):
        button_.disabled = True  # прекратить работу кнопки

        user_id: int = ctx.author.id
        WORKER_ORDER_CHANNEL: TextChannel = BOT.get_channel(SSBot.BOT_DATA["worker_order_channel_id"])

        # get client name
        SSBot.CLIENT_DB_CURSOR.execute("SELECT client_name FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_client_name = result[0] if result else None

        # get client id
        SSBot.CLIENT_DB_CURSOR.execute("SELECT client_id FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_client_id = result[0] if result else None

        # get client display name
        SSBot.CLIENT_DB_CURSOR.execute("SELECT client_display_name FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_client_display_name = result[0] if result else None

        # get service type
        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_type FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_service_type = result[0] if result else None

        # get service for gift
        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_for_gift FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_gift_service = result[0] if result else None

        # get service description
        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_description FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_service_description = result[0] if result else None

        # get service code
        SSBot.CLIENT_DB_CURSOR.execute("SELECT service_code FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_service_code = result[0] if result else None

        # get sending time
        SSBot.CLIENT_DB_CURSOR.execute("SELECT sending_time FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_sending_time = result[0] if result else None

        # get vk
        SSBot.CLIENT_DB_CURSOR.execute("SELECT vk_url FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_vk_url = result[0] if result else None

        # get mail
        SSBot.CLIENT_DB_CURSOR.execute("SELECT mail FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_mail = result[0] if result else None

        # get telegram url
        SSBot.CLIENT_DB_CURSOR.execute("SELECT telegram_url FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_telegram_url = result[0] if result else None

        # get active promo code
        SSBot.CLIENT_DB_CURSOR.execute("SELECT active_promo_code FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_active_promo_code = result[0] if result else None

        # get youtube promo code counter
        SSBot.CLIENT_DB_CURSOR.execute("SELECT youtube_promo_code_counter FROM settings WHERE user_id=?", (user_id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_youtube_promo_code_counter = result[0] if result else None

        color: Color = await utils.color_order(var_service_type)  # получение цвета для embed

        order_embed: Embed = Embed(title='Новый заказ:', color=color)
        order_embed.add_field(name=f'Код заказа: {var_service_code}\nДата оформления: {var_sending_time} (МСК / GMT+3)\nИмя заказчика: {var_client_display_name} (tag: {var_client_name})', value="")
        order_embed.add_field(name='Услуга:', value=await utils.convert_value_to_service_name(value=var_service_type), inline=False)
        order_embed.add_field(name='ID заказчика:', value=var_client_id, inline=False)

        if var_service_description is not None:
            order_embed.add_field(name="Описание:", value=var_service_description, inline=False)

        if var_active_promo_code is not None:
            order_embed.add_field(name="Активированный промокод:", value=var_active_promo_code, inline=False)

        if var_mail != "" and var_mail is not None or var_vk_url != "" and var_vk_url is not None or var_telegram_url != "" and var_telegram_url is not None:
            order_embed.add_field(name="Доп. контакты связи:", value="", inline=False)
            if var_vk_url != "" and var_vk_url is not None:
                order_embed.add_field(name=f'VK: {var_vk_url}', value="", inline=False)
            if var_telegram_url != "" and var_telegram_url is not None:
                order_embed.add_field(name=f'Telegram: {var_telegram_url}', value="", inline=False)
            if var_mail != "" and var_mail is not None:
                order_embed.add_field(name=f'Электронная почта: {var_mail}', value="", inline=False)

        pay_message_2: str = ""
        if var_active_promo_code is not None:
            promo_codes_data: dict = await utils.async_read_json(path=SSBot.PATH_TO_PROMO_CODES_DATA)  # получение данных о промокодах
            promo_code_type: str = promo_codes_data[var_active_promo_code]["type"]  # получение типа промокода
            sum_for_pay: int = int(await utils.calc_percentage(promo_code=var_active_promo_code, price=dicts.SERVICE_PRICES[var_service_type]))

            if promo_code_type == "common_code":
                self.__clear_promo_code_db(user_id=user_id)
                percentage = promo_codes_data[var_active_promo_code]["discount_rate"]
                pay_message_2 = f"\nТ.к. вы использовали промокод {var_active_promo_code} на скидку {percentage}%, то оплата будет в размере {sum_for_pay}₽."
            elif promo_code_type == "premium_code":
                percentage = promo_codes_data[var_active_promo_code]["discount_rate"]
                pay_message_2 = f"\nТ.к. вы использовали промокод {var_active_promo_code} на скидку {percentage}%, то оплата будет в размере {sum_for_pay}₽."
            elif promo_code_type == "aditi_service_code":
                self.__clear_promo_code_db(user_id=user_id)
                service = await utils.convert_value_to_service_name(promo_codes_data[var_active_promo_code]["service"])
                pay_message_2 = f'\nВы использовали промокод {var_active_promo_code} на дополнительную услугу {service} в подарок.'
                order_embed.add_field(name=f'(Промокод {var_active_promo_code} на доп. услугу {service})', value="", inline=False)

        if var_gift_service is not None:
            order_embed.add_field(name=f"Услуга для промокода: {await utils.convert_value_to_service_name(value=var_gift_service)}", value="")
            var_service: str = await utils.convert_value_to_service_name(value=var_gift_service)
        else:
            var_service: str = await utils.convert_value_to_service_name(value=var_service_type)

        avatar: Member.avatar = await utils.get_avatar(ctx_user_avatar=ctx.author.avatar)
        order_embed.set_author(name=var_client_display_name, icon_url=avatar)

        if var_youtube_promo_code_counter is not None:
            if var_youtube_promo_code_counter < 1:
                SSBot.CLIENT_DB_CURSOR.execute(
                    "INSERT INTO settings (user_id, promo_code_activated, youtube_promo_code_counter, active_promo_code) VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET promo_code_activated=?, active_promo_code=?, youtube_promo_code_counter=?",
                    (user_id, False, None, None, False, None, None)
                )
                SSBot.CLIENT_DB_CONNECTION.commit()
            else:
                var_youtube_promo_code_counter -= 1
                SSBot.CLIENT_DB_CURSOR.execute(
                    "INSERT INTO settings (user_id, youtube_promo_code_counter, promo_code_activated, active_promo_code) VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET youtube_promo_code_counter=?, promo_code_activated=?, active_promo_code=?",
                    (user_id, var_youtube_promo_code_counter, True, var_active_promo_code, var_youtube_promo_code_counter, True, var_active_promo_code)
                )
                SSBot.CLIENT_DB_CONNECTION.commit()

        if var_service in SSBot.NOT_STATIC_PRICE:
            pay_message: str = "Ваш заказ был отправлен мастерам SkylightServices. Скоро с вами свяжется один из мастеров."
            pay_message_2 = "\nСсылку для оплаты вам предоставят после связи с сотрудником."
        else:
            pay_message: str = "Ваш заказ был отправлен сотрудникам SkylightServices. Скоро с вами свяжется один из мастеров.\nСсылка для оплаты: https://www.donationalerts.com/r/skylightservice ."

        embed = Embed(title="Заказ отправлен", color=Color.blurple())
        embed.add_field(name="".join([pay_message, pay_message_2]), value="")

        try:
            pictures: list = await utils.get_files_disnake(f"cache/{ctx.author.name}/")
            await WORKER_ORDER_CHANNEL.send(embed=order_embed, view=TakeOrder(self.bot), files=pictures)
            await utils.delete_files_from_cache(author_name=ctx.author.name)
        except FileNotFoundError:
            await WORKER_ORDER_CHANNEL.send(embed=order_embed, view=TakeOrder(self.bot))

        await ctx.response.edit_message(view=self)
        await ctx.send(embed=embed)

    @button(label="Ввести промокод", style=ButtonStyle.blurple, custom_id="promo_code_button")
    async def promo_code_button(self, button_: Button, ctx: AppCmdInter):
        await ctx.response.send_modal(modal=PromoCodeEnterMenu(self.bot))

    def __clear_promo_code_db(self, user_id: int) -> None:
        SSBot.CLIENT_DB_CURSOR.execute(
            "INSERT INTO settings (user_id, promo_code_activated, youtube_promo_code_counter, active_promo_code) VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET promo_code_activated=?, active_promo_code=?, youtube_promo_code_counter=?",
            (user_id, False, None, None, False, None, None)
        )
        SSBot.CLIENT_DB_CONNECTION.commit()

    def to_components(self):
        return super().to_components()


def setup(bot):
    bot.add_cog(DonationAndPromoCodeButtonsReg(bot))
