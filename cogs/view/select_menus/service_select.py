import json

from disnake import Embed, SelectOption
from disnake.ext import commands
from disnake.ui import View
from disnake.ui.select.string import StringSelect
from pytz import timezone
from datetime import datetime

from main import SSBot
from cogs.hadlers import utils
from cogs.hadlers.dicts import SERVICE_PRICES, NOT_STATIC_PRICE
from cogs.view.buttons.enter_description_button import EnterDescriptionButton
from cogs.view.select_menus.promo_code_service_select import PromoCodeServiceSelectView


class ServiceSelectReg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ServiceSelect was added")
        self.bot.add_view(ServiceSelectView(bot=self.bot))


class ServiceSelect(StringSelect):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(
            placeholder="Список услуг", min_values=1, max_values=1,
            custom_id="service_select", options=[
                SelectOption(label=SSBot.SERVICES_NAME["skin64"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["skin64"]["code"]]}₽', value="skin64", emoji="🧍‍♂️"),
                SelectOption(label=SSBot.SERVICES_NAME["rew_skin"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["rew_skin"]["code"]]}₽', value="rew_skin", emoji="🧍‍♂️"),

                SelectOption(label=SSBot.SERVICES_NAME["model"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["model"]["code"]]}₽', value="model", emoji="\N{SNOWMAN}"),
                SelectOption(label=SSBot.SERVICES_NAME["anim_model"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["anim_model"]["code"]]}₽', value="anim_model", emoji="\N{SNOWMAN}"),
                SelectOption(label=SSBot.SERVICES_NAME["texture_model"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["texture_model"]["code"]]}₽', value="texture_model", emoji="\N{SNOWMAN}"),

                SelectOption(label=SSBot.SERVICES_NAME["cape"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["cape"]["code"]]}₽', value="cape", emoji="🧶"),
                SelectOption(label=SSBot.SERVICES_NAME["totem"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["totem"]["code"]]}₽', value="totem", emoji="🧶"),
                SelectOption(label=SSBot.SERVICES_NAME["texture"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["texture"]["code"]]}₽', value="texture", emoji="🧶"),

                SelectOption(label=SSBot.SERVICES_NAME["letter_logo"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["letter_logo"]["code"]]}₽', value="letter_logo", emoji="🆎"),
                SelectOption(label=SSBot.SERVICES_NAME["letter_logo_2"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["letter_logo_2"]["code"]]}₽', value="letter_logo_2", emoji="🆎"),

                SelectOption(label=SSBot.SERVICES_NAME["characters_design"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["characters_design"]["code"]]}₽', value="character_design", emoji="🥚"),
                SelectOption(label=SSBot.SERVICES_NAME["service_promocode"]["name"], description="", value="service_promocode", emoji="🥚")
            ]
        )

    async def callback(self, ctx):
        user_id = ctx.author.id

        async with ctx.channel.typing():

            with open(SSBot.PATH_TO_CODES, 'r') as file:  # загрузка файла с кодами заказов
                try:
                    codes = json.load(file)
                except json.JSONDecodeError:
                    codes = []

            # генерация и сохранение кода заказа
            combination = await utils.generate_random_combination(10)
            for element in codes:
                if combination in element["code"]:
                    combination = await utils.generate_random_combination(10)
                    continue
                else:
                    break
            codes.append({"code": combination})

            await utils.write_json(path=SSBot.PATH_TO_CODES, data=codes)

            current_time = datetime.now(tz=timezone('Europe/Moscow')).strftime("%d.%m.%Y %H:%M")  # получение отформатированной даты оформления заказа в ЧП МСК
            order_code = combination.replace("}", "").replace("{", "")  # Получение кода заказа

            SSBot.CLIENT_DB_CURSOR.execute("SELECT activated_promo_codes_list FROM settings WHERE user_id=?", (user_id,))
            result = SSBot.CLIENT_DB_CURSOR.fetchone()
            activated_promo_codes_list_var = result[0] if result else None

            if activated_promo_codes_list_var is None:
                SSBot.CLIENT_DB_CURSOR.execute(
                    "INSERT INTO settings (user_id, activated_promo_codes_list) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET activated_promo_codes_list=?",
                    (user_id, "1234567890,", "1234567890,")
                )
                SSBot.CLIENT_DB_CONNECTION.commit()

            author_avatar = str(await utils.get_avatar(ctx.author.avatar))

            SSBot.CLIENT_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, client_name, client_id, service_type, service_code, sending_time, client_display_name, client_avatar, mail, vk_url, telegram_url, can_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET client_name=?, client_id=?, service_type=?, service_code=?, sending_time=?, client_display_name=?, client_avatar=?, mail=?, vk_url=?, telegram_url=?, can_description=?",
                (user_id, ctx.author.name, ctx.author.id, self.values[0], order_code, current_time, ctx.author.display_name, author_avatar, None, None, None, False, ctx.author.name, ctx.author.id, self.values[0], order_code, current_time, ctx.author.display_name, author_avatar, None, None, None, False)
            )
            SSBot.CLIENT_DB_CONNECTION.commit()

            if self.values[0] != "service_promocode":
                embed = Embed(title="Проверка выбранной услуги", color=SSBot.DEFAULT_COLOR)
                embed.add_field(
                    name=f"Вы выбрали ***{await utils.convert_value_to_service_name(value=self.values[0])}***. Если вы по ошибке выбрали не ту услугу, то снова откройте список и выберите нужную вам.",
                    value="", inline=False
                )
                embed.add_field(
                    name="Для того, чтобы продолжить оформление заказа и начать описывать ваш желаемый результат, нажмите на кнопку \"Ввод описания\"",
                    value="", inline=False
                )

                view = EnterDescriptionButton(self.bot)
            else:
                embed: Embed = Embed(title="Оформление подарочного промокода", color=SSBot.DEFAULT_COLOR)
                embed.add_field(
                    name=f"Вы выбрали ***{await utils.convert_value_to_service_name(value=self.values[0])}***. Для того чтобы продолжить оформление подарочного промокода, выберите ниже услугу, к которой он должен относится:",
                    value="", inline=False
                )

                view = PromoCodeServiceSelectView(self.bot)

        await ctx.send(embed=embed, view=view)


class ServiceSelectView(View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(ServiceSelect(self.bot))


def setup(bot):
    bot.add_cog(ServiceSelectReg(bot))
