import json

from disnake import Embed, SelectOption
from disnake.ext import commands
from disnake.ui import View
from disnake.ui.select.string import StringSelect
from sqlite3 import connect
from pytz import timezone
from datetime import datetime

from main import SSBot
from cogs.hadlers import utils, dicts
from cogs.view.buttons.enter_description_button import EnterDescriptionButton


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
                SelectOption(label=SSBot.SKIN64, description=f"{dicts.SERVICE_PRICES[SSBot.SKIN64]}₽", emoji="🧍‍♂️"),
                # disnake.SelectOption(label="Скин 128x128", emoji="🧍‍♂️"),
                # disnake.SelectOption(label="4D скин", emoji="🧍‍♂️"),

                SelectOption(label=SSBot.MODEL, description=f"от {dicts.NOT_STATIC_PRICE[SSBot.MODEL]}₽", emoji="\N{SNOWMAN}"),
                SelectOption(label=SSBot.ANIM_MODEL, description=f"от {dicts.NOT_STATIC_PRICE[SSBot.ANIM_MODEL]}₽", emoji="\N{SNOWMAN}"),
                SelectOption(label=SSBot.TEXTURE_MODEL, description=f"от {dicts.NOT_STATIC_PRICE[SSBot.TEXTURE_MODEL]}₽", emoji="\N{SNOWMAN}"),
                # disnake.SelectOption(label="Модель + GeckoLib анимация + текстура", description="",  emoji="\N{SNOWMAN}"),

                SelectOption(label=SSBot.CAPE, description=f"{dicts.SERVICE_PRICES[SSBot.CAPE]}₽", emoji="🧶"),
                SelectOption(label=SSBot.TOTEM, description=f"{dicts.SERVICE_PRICES[SSBot.TOTEM]}₽", emoji="🧶"),
                # disnake.SelectOption(label="3D тотем со скином игрока", description="", emoji="🧶"),
                SelectOption(label=SSBot.TEXTURE, description=f"{dicts.SERVICE_PRICES[SSBot.TEXTURE]}₽", emoji="🧶"),

                SelectOption(label=SSBot.LETTER_LOGO, description=f"{dicts.SERVICE_PRICES[SSBot.LETTER_LOGO]}₽", emoji="🆎"),
                SelectOption(label=SSBot.LETTER_LOGO_2, description=f"от {dicts.NOT_STATIC_PRICE[SSBot.LETTER_LOGO_2]}₽", emoji="🆎"),

                SelectOption(label=SSBot.CHARACTERS_DESIGN, description=f"{dicts.SERVICE_PRICES[SSBot.CHARACTERS_DESIGN]}₽", emoji="🥚"),

                # disnake.SelectOption(label=SSBot.SPIGOT_PLUGIN, description=dicts.NOT_STATIC_PRICE[SSBot.SPIGOT_PLUGIN], emoji="💻"),
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
                if combination in element:
                    combination = await utils.generate_random_combination(10)
                    continue
                else:
                    break
            codes.append({"code": combination})

            with open(SSBot.PATH_TO_CODES, 'w') as file:  # сохранение файла с кодами заказа
                json.dump(codes, file)

            # moscow_tz = pytz.timezone('Europe/Moscow')
            current_time = datetime.now(tz=timezone('Europe/Moscow'))  # Создание ориентира на часовой пояс МСК
            order_time = current_time.strftime("%d.%m.%Y %H:%M")  # получение даты оформления заказа

            order_code = combination.replace("}", "").replace("{", "")  # Получение кода заказа

            connection = connect(SSBot.PATH_TO_CLIENT_DB)
            cursor = connection.cursor()
            cursor.execute("SELECT activated_promo_codes_list FROM settings WHERE user_id=?", (user_id,))
            result = cursor.fetchone()
            activated_promo_codes_list_var = result[0] if result else None
            connection.close()

            if activated_promo_codes_list_var is None:
                connection_ = connect(SSBot.PATH_TO_CLIENT_DB)
                cursor_ = connection_.cursor()
                cursor_.execute(
                    "INSERT INTO settings (user_id, activated_promo_codes_list) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET activated_promo_codes_list=?",
                    (user_id, "1234567890,", "1234567890,")
                )
                connection_.commit()
                connection_.close()

            connection = connect(SSBot.PATH_TO_CLIENT_DB)
            cursor = connection.cursor()
            try:  # если у пользователя есть аватар, то тогда ссылка на него сохранится в переменную
                author_avatar = str(ctx.author.avatar.url)
            except AttributeError:
                author_avatar = None
            cursor.execute(
                "INSERT INTO settings (user_id, client_name, client_id, service_type, service_code, sending_time, client_display_name, client_avatar, mail, vk_url, telegram_url, can_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET client_name=?, client_id=?, service_type=?, service_code=?, sending_time=?, client_display_name=?, client_avatar=?, mail=?, vk_url=?, telegram_url=?, can_description=?",
                (user_id, ctx.author.name, ctx.author.id, self.values[0], order_code, order_time, ctx.author.display_name, author_avatar, None, None, None, False, ctx.author.name, ctx.author.id, self.values[0], order_code, order_time, ctx.author.display_name, author_avatar, None, None, None, False)
            )
            connection.commit()
            connection.close()

            embed = Embed(title="Проверка выбранной услуги", color=SSBot.DEFAULT_COLOR)
            embed.add_field(
                name=f"Вы выбрали ***{self.values[0]}***. Если вы по ошибке выбрали не ту услугу, то снова откройте список и выберите нужную вам.",
                value="", inline=False
            )
            embed.add_field(
                name="Для того, чтобы продолжить оформление заказа и начать описывать ваш желаемый результат, нажмите на кнопку \"Ввод описания\"",
                value="", inline=False
            )

        await ctx.send(embed=embed, view=EnterDescriptionButton(self.bot))


class ServiceSelectView(View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(ServiceSelect(self.bot))


def setup(bot):
    bot.add_cog(ServiceSelectReg(bot))
