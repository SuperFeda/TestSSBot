import disnake, json

from datetime import datetime
from pytz import timezone
from disnake.ext import commands

from cogs.view.buttons.enter_description_button import EnterDescriptionButton
from main import SSBot
from cogs.hadlers import utils


class ContinueAndCancelButtonsReg(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ContinueAndCancelButtons was added")
        self.bot.add_view(ContinueAndCancelButtons(self.bot, promo_code="", service=""))


class ContinueAndCancelButtons(disnake.ui.View):

    def __init__(self, bot: commands.Bot, promo_code: str, service: str):
        self.bot = bot
        self.promo_code = promo_code
        self.service = service
        super().__init__(timeout=None)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.green, custom_id="continue_button_cacb")
    async def continue_button_cacb(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        user_id: int = ctx.author.id

        async with ctx.channel.typing():

            SSBot.CLIENT_DB_CURSOR.execute("SELECT activated_promo_codes_list FROM settings WHERE user_id=?", (user_id,))
            result = SSBot.CLIENT_DB_CURSOR.fetchone()
            activated_promo_codes_list_var = result[0] if result else None

            if activated_promo_codes_list_var is not None:
                new_activated_promo_codes_list = activated_promo_codes_list_var + self.promo_code+","
            else:
                new_activated_promo_codes_list = f"1234567890,{self.promo_code},"

            SSBot.CLIENT_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, activated_promo_codes_list) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET activated_promo_codes_list=?",
                (user_id, new_activated_promo_codes_list, new_activated_promo_codes_list,)
            )
            SSBot.CLIENT_DB_CONNECTION.commit()

            with open(SSBot.PATH_TO_CODES, 'r') as file:  # загрузка файла с кодами заказов
                try:
                    codes = json.load(file)
                except json.JSONDecodeError:
                    codes = []

            # генерация и сохранение кода заказа
            combination = await utils.generate_random_combination(10)
            for element in codes:
                if combination in element["code"]:
                    print(element["code"])
                    combination = await utils.generate_random_combination(10)
                    continue
                else:
                    break
            codes.append({"code": combination})

            await utils.write_json(path=SSBot.PATH_TO_CODES, data=codes)

            current_time = datetime.now(tz=timezone('Europe/Moscow')).strftime("%d.%m.%Y %H:%M")  # получение отформатированной даты оформления заказа в ЧП МСК
            order_code = combination.replace("}", "").replace("{", "")  # Получение кода заказа

            author_avatar = str(await utils.get_avatar(ctx.author.avatar))

            SSBot.CLIENT_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, client_name, client_id, service_type, service_code, sending_time, client_display_name, client_avatar, mail, vk_url, telegram_url, can_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET client_name=?, client_id=?, service_type=?, service_code=?, sending_time=?, client_display_name=?, client_avatar=?, mail=?, vk_url=?, telegram_url=?, can_description=?",
                (user_id, ctx.author.name, ctx.author.id, self.service, order_code, current_time, ctx.author.display_name, author_avatar, None, None, None, False, ctx.author.name, ctx.author.id, self.service, order_code, current_time, ctx.author.display_name, author_avatar, None, None, None, False)
            )
            SSBot.CLIENT_DB_CONNECTION.commit()

            embed = disnake.Embed(title="Проверка выбранной услуги", color=SSBot.DEFAULT_COLOR)
            embed.add_field(
                name="Для того, чтобы продолжить оформление заказа и начать описывать ваш желаемый результат, нажмите на кнопку \"Ввод описания\"",
                value="", inline=False
            )

        await ctx.send(embed=embed, view=EnterDescriptionButton(self.bot))

    @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.red, custom_id="cancel_button_cacb")
    async def cancel_button_cacb(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        embed: disnake.Embed = utils.create_embed(title="Операция отменена", color=disnake.Color.red(), content="Операция оформления заказа с подарочным промокодом отменена.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ContinueAndCancelButtonsReg(bot))

