from disnake import (
    utils as disnake_utils,
    ButtonStyle,
    PermissionOverwrite,
    Member,
    Message,
    CategoryChannel,
    TextChannel,
    Embed,
    MessageInteraction
)
from disnake.ui import View
from disnake.ui.button import button, Button
from disnake.ext.commands import Cog

from main import SSBot
from cogs.hadlers import utils as bot_utils, dicts
from cogs.hadlers.embeds import question_embeds


class TakeOrderReg(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("TakeOrder was added")
        self.bot.add_view(TakeOrder(bot=self.bot))


class TakeOrder(View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @button(label="Принять", style=ButtonStyle.green, custom_id="take_order_button")
    async def take_order_button(self, button_: Button, ctx: MessageInteraction):
        category: CategoryChannel = disnake_utils.get(ctx.guild.categories, id=SSBot.BOT_DATA["orders_category_id"])  # получение категории, в которой в будущем нужно создать канал
        client_order_message: Message = await ctx.channel.fetch_message(ctx.message.id)  # получение ctx сообщения для будущего редактирования
        service_type_from_embed: str = client_order_message.embeds[0]._fields[1]["value"]  # получение заказанной клиентом услуги
        client_id_from_embed: int = int(client_order_message.embeds[0]._fields[2]["value"])  # получение id клиента
        avatar: Member.avatar = await bot_utils.get_avatar(ctx_user_avatar=ctx.author.avatar)  # аватар заказчика
        owner: Member = ctx.guild.get_member(SSBot.BOT_DATA["owner_id"])  # получение владельца SS как объект Member
        enter_promo_code_from_embed: str = ''
        promo_code_type: str = ''
        worker_id: int = ctx.author.id  # id пользователя принявшего заказ
        flag: bool = False  # флаг благодаря которому определяется, ввел ли заказчик промокод

        try:
            field_4_data: dict = client_order_message.embeds[0]._fields[4]
            if field_4_data["name"] == "Активированный промокод:":
                enter_promo_code_from_embed = field_4_data["value"]
                flag = True
        except IndexError or KeyError:
            pass

        if enter_promo_code_from_embed is not None and enter_promo_code_from_embed != "":
            promo_code_type = await bot_utils.get_promocode_type(enter_promo_code_from_embed)

        # find client name
        SSBot.CLIENT_DB_CURSOR.execute("SELECT client_name FROM settings WHERE user_id=?", (client_id_from_embed,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        var_client_name = result[0] if result else None

        try:  # если работник находится в базе данных:
            # var_worker_salary
            SSBot.WORKER_DB_CURSOR.execute("SELECT worker_salary FROM settings WHERE user_id=?", (worker_id,))
            result_ = SSBot.WORKER_DB_CURSOR.fetchone()
            var_worker_salary = result_[0] if result_ else None

            var_worker_salary: int = int(var_worker_salary)

            new_worker_salary: int = var_worker_salary + dicts.SUMM_WORKER[service_type_from_embed]

            SSBot.WORKER_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, worker_salary) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?",
                (worker_id, new_worker_salary, new_worker_salary)
            )
            SSBot.WORKER_DB_CONNECTION.commit()

            await self.__save_owner_salary(  # summ_for_owner
                flag=flag,
                owner=owner,
                promo_code_type=promo_code_type,
                service_type=service_type_from_embed,
                enter_promo_code=enter_promo_code_from_embed,
                worker_salary=var_worker_salary,
                new_worker_salary=new_worker_salary
            )

        except TypeError:  # иначе: запись всех данных о сотруднике
            var_worker_salary_2 = dicts.SUMM_WORKER[service_type_from_embed]

            await self.__save_owner_salary(  # summ_for_owner
                flag=flag,
                owner=owner,
                promo_code_type=promo_code_type,
                service_type=service_type_from_embed,
                enter_promo_code=enter_promo_code_from_embed
            )

            await bot_utils.var_test(var_worker_salary_2)

            SSBot.WORKER_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, worker_salary, worker_tag, worker_display_name, worker_id) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?, worker_tag=?, worker_display_name=?, worker_id=?",
                (worker_id, var_worker_salary_2, ctx.author.name, ctx.author.display_name, ctx.author.id, var_worker_salary_2, ctx.author.name, ctx.author.display_name, ctx.author.id)
            )
            SSBot.WORKER_DB_CONNECTION.commit()

        if ctx.author.id == client_id_from_embed:
            permissions = {
                ctx.guild.default_role: PermissionOverwrite(read_messages=False, view_channel=False, send_messages=False),
                ctx.author: PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
            }
        else:
            permissions = {
                ctx.guild.default_role: PermissionOverwrite(read_messages=False, view_channel=False, send_messages=False),
                ctx.author: PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
                ctx.guild.get_member(client_id_from_embed): PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
            }

        channel: TextChannel = await ctx.guild.create_text_channel(
            name=f"{var_client_name}-{service_type_from_embed}",
            category=category, overwrites=permissions
        )

        embed: Embed = client_order_message.embeds[0]
        embed.set_footer(text=f"Заказ принял: {ctx.author.display_name}", icon_url=avatar)

        if service_type_from_embed == SSBot.SKIN64:
            await channel.send(f"<@{client_id_from_embed}> ,", embed=question_embeds.SKIN_QUESTION_EMBED)
        elif service_type_from_embed == SSBot.TOTEM:
            await channel.send(f"<@{client_id_from_embed}> ,", embed=question_embeds.TOTEM_QUESTION_EMBED)
        elif service_type_from_embed in (SSBot.LETTER_LOGO, SSBot.LETTER_LOGO_2):
            await channel.send(f"<@{client_id_from_embed}> ,", embed=question_embeds.LOGO_QUESTION_EMBED, file=question_embeds.LOGOS)
        elif service_type_from_embed == SSBot.CHARACTERS_DESIGN:
            await channel.send(f"<@{client_id_from_embed}> ,", embed=question_embeds.CHARACTERS_QUESTION_EMBED)
        else:
            await channel.send(f"<@{client_id_from_embed}>")

        # elif service_type_from_embed == SSBot.TEXTURE:
        #     texture_questions = disnake.Embed(
        #         title="Дополнительные вопросы",
        #         color=SSBot.DEFAULT_COLOR,
        #         description="Для того чтобы мы выполнили ваш заказа так, как хотите вы, нам нужно знать ещё кое-какую информацию. Пожалуйста, ответьте на вопросы ниже:"
        #     ).add_field(name="1) Какое должно быть качество у текстуры: 16х16 или 32х32?", value="", inline=False)
        #
        #     await channel.send(f"<@{client_id_from_embed}> ,", embed=texture_questions)

        await channel.send(f"<@{ctx.author.id}>")
        await client_order_message.edit(embed=embed, view=None)

    # async def __get_value_from_embed(self, data: dict) -> str:
    #     """
    #     Получение определенного значения из Embed
    #     :param data: данные из которых нужно вытащить значение
    #     :return: значение
    #     """
    #     return data["value"]

    async def __save_owner_salary(self, flag: bool, owner: Member, promo_code_type: str, service_type: str, enter_promo_code: str, worker_salary: int = 0, new_worker_salary: int = 0) -> None:
        """
        Костыльная функция для сохранения зарплаты для владельца
        :param flag: специальный флаг для работы с промокодом типа `service_code`
        :param owner: владелец
        :param promo_code_type: тип промокода
        :param service_type: название услуги
        :param enter_promo_code: введенный промокод
        :param worker_salary: зарплата сотрудника
        :param new_worker_salary: новая зарплата сотрудника
        :return: None
        """
        try:
            SSBot.WORKER_DB_CURSOR.execute("SELECT worker_salary FROM settings WHERE user_id=?", (owner.id,))
            result_ = SSBot.WORKER_DB_CURSOR.fetchone()
            var_owner_sum = result_[0] if result_ else None

            if flag is True and promo_code_type != "service_code":  # Проверить как всё сохраняется во время заказа услуги с нестат. ценником и промокодом
                summ_for_owner: int = (dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]) + int(await bot_utils.calc_percentage(promo_code=enter_promo_code, price=dicts.SERVICE_PRICES[service_type]))
            else:
                summ_for_owner: int = dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]

            var_owner_sum = var_owner_sum + summ_for_owner

            await bot_utils.var_test(var_owner_sum)
            await bot_utils.var_test(worker_salary)
            await bot_utils.var_test(new_worker_salary)

            SSBot.WORKER_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, worker_salary) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?",
                (owner.id, var_owner_sum, var_owner_sum)
            )
            SSBot.WORKER_DB_CONNECTION.commit()
        except TypeError:
            if flag is True and promo_code_type != "service_code":  # Проверить как всё сохраняется во время заказа услуги с нестат. ценником и промокодом
                summ_for_owner: int = (dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]) + int(await bot_utils.calc_percentage(promo_code=enter_promo_code, price=dicts.SERVICE_PRICES[service_type]))
            else:
                summ_for_owner: int = dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]

            await bot_utils.var_test(worker_salary)
            await bot_utils.var_test(new_worker_salary)

            SSBot.WORKER_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, worker_salary, worker_tag, worker_display_name, worker_id) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?, worker_tag=?, worker_display_name=?, worker_id=?",
                (owner.id, summ_for_owner, owner.name, owner.display_name, owner.id, summ_for_owner, owner.name, owner.display_name, owner.id)
            )
            SSBot.WORKER_DB_CONNECTION.commit()

    def to_components(self):
        return super().to_components()


def setup(bot):
    bot.add_cog(TakeOrderReg(bot))
