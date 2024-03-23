from sqlite3 import connect
from disnake import utils, ButtonStyle, PermissionOverwrite, Member
from disnake.ui import View
from disnake.ui.button import button, Button
from disnake.ext.commands import Cog

from main import SSBot
from cogs.hadlers import dicts, utils as bot_utils
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
    async def take_order_button(self, button_: Button, ctx):
        category = utils.get(ctx.guild.categories, id=SSBot.BOT_DATA["orders_category_id"])
        client_order_message = await ctx.channel.fetch_message(ctx.message.id)
        service_type_from_embed = await self.for_in_embed(in_=client_order_message.embeds[0]._fields[1].items())  # getting client service type from embed
        client_id_from_embed = int(await self.for_in_embed(in_=client_order_message.embeds[0]._fields[2].items()))  # getting client id from his order embed
        avatar = await bot_utils.get_avatar(ctx_user_avatar=ctx.author.avatar)
        owner = ctx.guild.get_member(SSBot.BOT_DATA["owner_id"])
        promo_code_type = None
        worker_id = ctx.author.id

        enter_promo_code_from_embed = None
        flag, flag_2 = False, False

        try:
            for key_, value_ in client_order_message.embeds[0]._fields[4].items():  # получение введенного промокода из embed
                if key_ == "name" and value_ == "Активированный промокод:":
                    flag_2 = True
                if key_ == "value" and flag_2 is True:
                    enter_promo_code_from_embed = value_
                    flag = True
                    break
        except IndexError:
            pass

        if enter_promo_code_from_embed is not None:
            promo_code_type = await bot_utils.get_promocode_type(enter_promo_code_from_embed)

        connection = connect(SSBot.PATH_TO_CLIENT_DB)
        cursor = connection.cursor()

        # find client name
        cursor.execute("SELECT client_name FROM settings WHERE user_id=?", (client_id_from_embed,))
        result = cursor.fetchone()
        var_client_name = result[0] if result else None

        connection.close()

        try:  # если работник находится в базе данных:
            # var_worker_salary
            connection_ = connect(SSBot.PATH_TO_WORKER_DB)
            cursor_ = connection_.cursor()
            cursor_.execute("SELECT worker_salary FROM settings WHERE user_id=?", (worker_id,))
            result_ = cursor_.fetchone()
            var_worker_salary = result_[0] if result_ else None
            connection_.close()

            var_worker_salary = int(var_worker_salary)

            new_worker_salary = var_worker_salary + dicts.SUMM_WORKER[service_type_from_embed]

            connection_ = connect(SSBot.PATH_TO_WORKER_DB)
            cursor_ = connection_.cursor()
            cursor_.execute(
                "INSERT INTO settings (user_id, worker_salary) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?",
                (worker_id, new_worker_salary, new_worker_salary)
            )
            connection_.commit()
            connection_.close()

            await self.save_owner_salary(  # summ_for_owner
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

            await self.save_owner_salary(  # summ_for_owner
                flag=flag,
                owner=owner,
                promo_code_type=promo_code_type,
                service_type=service_type_from_embed,
                enter_promo_code=enter_promo_code_from_embed
            )

            await bot_utils.var_test(var_worker_salary_2)

            connection_ = connect(SSBot.PATH_TO_WORKER_DB)
            cursor_ = connection_.cursor()
            cursor_.execute(
                "INSERT INTO settings (user_id, worker_salary, worker_tag, worker_display_name, worker_id) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?, worker_tag=?, worker_display_name=?, worker_id=?",
                (worker_id, var_worker_salary_2, ctx.author.name, ctx.author.display_name, ctx.author.id, var_worker_salary_2, ctx.author.name, ctx.author.display_name, ctx.author.id)
            )
            connection_.commit()
            connection_.close()

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

        channel = await ctx.guild.create_text_channel(
            name=f"{var_client_name}-{service_type_from_embed}",
            category=category, overwrites=permissions
        )

        embed = client_order_message.embeds[0]
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

    async def for_in_embed(self, in_: dict) -> str:
        data = None
        for key_, value_ in in_:
            if key_ == "value":
                data = value_
                break

        return data

    async def save_owner_salary(self, flag: bool, owner: Member, promo_code_type: str, service_type: str, enter_promo_code: str, worker_salary: int | None = None, new_worker_salary: int | None = None) -> None:
        try:
            connection_ = connect(SSBot.PATH_TO_WORKER_DB)
            cursor_ = connection_.cursor()
            cursor_.execute("SELECT worker_salary FROM settings WHERE user_id=?", (owner.id,))
            result_ = cursor_.fetchone()
            var_owner_sum = result_[0] if result_ else None
            connection_.close()

            if flag is True and promo_code_type != "service_code":  # Проверить как всё сохраняется во время заказа услуги с нестат. ценником и промокодом
                summ_for_owner = (dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]) + int(await bot_utils.calc_percentage(promo_code=enter_promo_code, price=dicts.SERVICE_PRICES[service_type]))
            else:
                summ_for_owner = dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]

            var_owner_sum = var_owner_sum + summ_for_owner

            await bot_utils.var_test(var_owner_sum)
            await bot_utils.var_test(worker_salary)
            await bot_utils.var_test(new_worker_salary)

            connection_ = connect(SSBot.PATH_TO_WORKER_DB)
            cursor_ = connection_.cursor()
            cursor_.execute(
                "INSERT INTO settings (user_id, worker_salary) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?",
                (owner.id, var_owner_sum, var_owner_sum)
            )
            connection_.commit()
            connection_.close()
        except TypeError:
            if flag is True and promo_code_type != "service_code":  # Проверить как всё сохраняется во время заказа услуги с нестат. ценником и промокодом
                summ_for_owner = (dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]) + int(await bot_utils.calc_percentage(promo_code=enter_promo_code, price=dicts.SERVICE_PRICES[service_type]))
            else:
                summ_for_owner = dicts.SERVICE_PRICES[service_type] - dicts.SUMM_WORKER[service_type]

            await bot_utils.var_test(worker_salary)
            await bot_utils.var_test(new_worker_salary)

            connection_ = connect(SSBot.PATH_TO_WORKER_DB)
            cursor_ = connection_.cursor()
            cursor_.execute(
                "INSERT INTO settings (user_id, worker_salary, worker_tag, worker_display_name, worker_id) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?, worker_tag=?, worker_display_name=?, worker_id=?",
                (owner.id, summ_for_owner, owner.name, owner.display_name, owner.id, summ_for_owner, owner.name, owner.display_name, owner.id)
            )
            connection_.commit()
            connection_.close()

    def to_components(self):
        return super().to_components()


def setup(bot):
    bot.add_cog(TakeOrderReg(bot))
