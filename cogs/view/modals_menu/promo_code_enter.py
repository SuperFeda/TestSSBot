from disnake import Embed, TextInputStyle, ModalInteraction, Color
from disnake.ui.modal import Modal, TextInput
from datetime import datetime
from pytz import timezone
from disnake.ext.commands import Cog

from main import SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds import template_embeds


class PromoCodeEnterMenuReg(Cog):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("PromoCodeEnterMenu was added")
        self.bot.add_view(PromoCodeEnterMenu(bot=self.bot))


class PromoCodeEnterMenu(Modal):

    def __init__(self, bot):
        self.bot = bot
        super().__init__(
            title="Ввод промокода", custom_id="promo_code_enter",
            timeout=300.0, components=[
                TextInput(
                    label="Промокод",
                    placeholder="Введите промокод",
                    custom_id="promo_code",
                    style=TextInputStyle.short,
                    max_length=50,
                )
            ]
        )

    async def callback(self, ctx: ModalInteraction):
        promo_codes_data: dict = await utils.async_read_json(path=SSBot.PATH_TO_PROMO_CODES_DATA)  # подгрузка файла с данными о промокодами
        entered_promo_code: str = ctx.text_values["promo_code"]  # Получение данных введенных в TextInput под id "promo_code" в модальном меню
        user_id: int = ctx.author.id

        try:
            promo_code_type: str = promo_codes_data[entered_promo_code]["type"]  # Получение типа промокода
        except KeyError:
            return await ctx.send(embed=template_embeds.WARN_PROMO_CODE_NOT_IN_DB)

        if entered_promo_code not in promo_codes_data:
            return await ctx.send(embed=template_embeds.WARN_PROMO_CODE_NOT_IN_DB)
        if promo_code_type == "service_code":
            __embed: Embed = utils.create_embed(title="Не подходящий тип промокода", color=Color.red(), content="Вы ввели подарочный промокод, но проблема в том, что его нужно было вводить в самом начале оформления заказа нажав на кнопку \"Ввести промокод\".\nВы можете ввести другой промокод, либо вернуться в начало и переоформить заказ.")
            return await ctx.send(embed=__embed)

        async with ctx.channel.typing():
            # Получение значения, которое говорит, есть ли уже активный промокод у мембера или нет
            SSBot.CLIENT_DB_CURSOR.execute("SELECT promo_code_activated FROM settings WHERE user_id=?", (user_id,))
            result = SSBot.CLIENT_DB_CURSOR.fetchone()
            promo_code_activated_var = result[0] if result else None

            # Найти список с веденными промокодами
            SSBot.CLIENT_DB_CURSOR.execute("SELECT activated_promo_codes_list FROM settings WHERE user_id=?", (user_id,))
            result = SSBot.CLIENT_DB_CURSOR.fetchone()
            activated_promo_codes_list_var = result[0] if result else None

            user_codes: list = await utils.string_to_list(activated_promo_codes_list_var)
            if entered_promo_code in user_codes:
                return await ctx.send(embed=template_embeds.WARN_PROMO_CODE_WAS_PREVIOUSLY_ENTERED_EMBED)

            if promo_code_activated_var is True or promo_code_activated_var == 1:
                return await ctx.send(embed=template_embeds.WARN_ACTIVATED_PROMO_CODE_AVAILABLE_EMBED)

            user_can_activate_promo_code_flag: bool = False
            premium_codes_count_var: int | None = promo_codes_data[entered_promo_code]["count"] if promo_code_type == "premium_code" else None

            if "users" in promo_codes_data[entered_promo_code]:
                for pr_user_id in promo_codes_data[entered_promo_code]["users"]:
                    if pr_user_id == user_id:
                        user_can_activate_promo_code_flag = True
                        break
                if user_can_activate_promo_code_flag is False:
                    return await ctx.send(embed=template_embeds.WARN_USER_NOT_IN_LIST)

            if "count_for_use" in promo_codes_data[entered_promo_code]:
                if promo_codes_data[entered_promo_code]["count_for_use"] < 1:
                    return await ctx.send(embed=template_embeds.WARN_PROMO_CODE_CANNOT_BE_USED)
                promo_codes_data[entered_promo_code]["count_for_use"] -= 1
                await utils.write_json(SSBot.PATH_TO_PROMO_CODES_DATA, promo_codes_data)

            if "time" in promo_codes_data[entered_promo_code]:
                current_time: datetime = datetime.now(tz=timezone("Europe/Moscow"))  # получение текущего времени по МСК
                promo_code_end_time: datetime = datetime.strptime(promo_codes_data[entered_promo_code]["time"], "%d.%m.%Y %H:%M")  # превращение даты из данных промокода в объект datetime для дальнейшего сравнения
                if current_time.timestamp() >= promo_code_end_time.timestamp():
                    # promo_codes_data.pop(entered_promo_code)
                    # await utils.write_json(SSBot.PATH_TO_PROMO_CODES_DATA, promo_codes_data)
                    return await ctx.send(embed=template_embeds.PROMO_CODE_TIME_IS_END)

            activated_promo_codes_list_var += entered_promo_code+","  # Создание списка введенных промокодов

            SSBot.CLIENT_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, promo_code_activated, activated_promo_codes_list, active_promo_code, youtube_promo_code_counter) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET promo_code_activated=?, activated_promo_codes_list=?, active_promo_code=?, youtube_promo_code_counter=?",
                (user_id, True, activated_promo_codes_list_var, entered_promo_code, premium_codes_count_var, True, activated_promo_codes_list_var, entered_promo_code, premium_codes_count_var)
            )
            SSBot.CLIENT_DB_CONNECTION.commit()

            promo_code_activated = utils.create_embed(
                title="Промокод активирован",
                color=SSBot.DEFAULT_COLOR,
                content=f"Промокод {entered_promo_code} успешно активирован."
            )
        await ctx.send(embed=promo_code_activated)


def setup(bot):
    bot.add_cog(PromoCodeEnterMenuReg(bot))
