import disnake, sqlite3

from disnake.ext import commands
from disnake import Localized

from main import SSBot
from cogs.hadlers import utils, bot_choices
from cogs.hadlers.embeds import template_embeds


class OwnerCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="get_salary_list")
    async def get_salary_list(self, ctx):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        connection = sqlite3.connect(SSBot.PATH_TO_WORKER_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM settings")
        result = cursor.fetchall()
        connection.close()

        workers_salary_embed = disnake.Embed(title="Список зарплат:", colour=disnake.Color.blurple())
        for num, item in enumerate(result):
            workers_salary_embed.add_field(name=f"{num+1}) {item[3]} ({item[2]}): {item[1]}₽", value="", inline=False)

        await ctx.send(embed=workers_salary_embed, ephemeral=True)

    @commands.slash_command(name="reset_all_workers_salary")
    async def reset_all_workers_salary(self, ctx):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        connection = sqlite3.connect(SSBot.PATH_TO_WORKER_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM settings")
        result = cursor.fetchall()
        connection.close()

        for item in result:
            connection = sqlite3.connect(SSBot.PATH_TO_WORKER_DB)
            cursor = connection.cursor()
            user_id = item[0]
            cursor.execute(
                "INSERT INTO settings (user_id, worker_salary) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?",
                (user_id, 0, 0)
            )
            connection.commit()
            connection.close()

        await ctx.send(embed=template_embeds.SALARIES_CANCELLED_EMBED, ephemeral=True)

    @commands.slash_command(name="edit_one_worker_salary")
    async def edit_one_worker_salary(self, ctx, worker: disnake.Member, salary: int):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        user_id = worker.id

        connection = sqlite3.connect(SSBot.PATH_TO_WORKER_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT worker_salary FROM settings WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        var_worker_salary = result[0] if result else None
        connection.close()

        connection = sqlite3.connect(SSBot.PATH_TO_WORKER_DB)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO settings (user_id, worker_salary) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?",
            (user_id, salary, salary)
        )
        connection.commit()
        connection.close()

        avatar = utils.get_avatar(worker.avatar)

        embed = (disnake.Embed(title="Зарплата изменена", color=disnake.Color.blurple())
                 .set_author(name=worker.display_name, icon_url=avatar)
                 .add_field(name=f"Зарплата для {worker.display_name} изменена с {var_worker_salary}₽ на {salary}₽", value=""))

        await ctx.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="edit_all_worker_salary")
    async def edit_all_worker_salary(self, ctx, salary: int, sure: bool = commands.Param(choices=bot_choices.CHOICE_FOR_SURE, description=Localized("Are you sure?", key="edit_all_worker_salary.sure.description"))):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        if sure is False or sure is None:
            embed = utils.create_embed(title="Отказано", color=disnake.Color.red(), content=f"{sure = }")
            return await ctx.send(embed=embed, ephemeral=True)

        connection = sqlite3.connect(SSBot.PATH_TO_WORKER_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM settings")
        result = cursor.fetchall()
        connection.close()

        embed = disnake.Embed(title="Изменения зарплат:", color=disnake.Color.blurple())

        for item in result:
            embed.add_field(name=f"Зарплата {item[3]} ({item[2]}) изменена с {item[1]}₽ на {salary}₽", value='', inline=False)

            connection = sqlite3.connect(SSBot.PATH_TO_WORKER_DB)
            cursor = connection.cursor()
            user_id = item[0]
            cursor.execute(
                "INSERT INTO settings (user_id, worker_salary) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET worker_salary=?",
                (user_id, salary, salary)
            )
            connection.commit()
            connection.close()

        await ctx.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="for_delete")
    async def for_delete(self, ctx):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        await ctx.channel.purge()

    @commands.slash_command(name="add_promo_code")
    async def add_promo_code(
            self, ctx, promo_code_name: str, discount_rate: int, service: str | None = None, count: int | None = None,
            count_for_use: int | None = None, date: str | None = commands.Param(default=None, description="Format: day.month.year"),
            pc_type: str = commands.Param(choices=bot_choices.CHOICE_FOR_PC_TYPE)
    ):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        pc_data = await utils.async_read_json(path=SSBot.PATH_TO_PROMO_CODES_DATA)

        if promo_code_name in pc_data:
            return await ctx.send(f"Промокод **{promo_code_name}** уже есть в базе данных.", ephemeral=True)

        if pc_type == "common_code":
            if discount_rate > 99:
                return await ctx.send("`discount_rate` должен быть не больше 99%!", ephemeral=True)
            if count is not None:
                return await ctx.send("Промокоды категории \"`common_code`\" не поддерживают count!", ephemeral=True)

            pc_data.update({promo_code_name: {"discount_rate": discount_rate, "type": pc_type}})

        elif pc_type == "premium_code":
            if count is None:
                return await ctx.send("Для промокода типа \"`premium_code`\" параметр \"`count`\" - обязателен!", ephemeral=True)
            if count < 2:
                return await ctx.send("count должен иметь значение не меньше 2!", ephemeral=True)
            if discount_rate > 40:
                return await ctx.send("`discount_rate` должен быть не больше 40%!", ephemeral=True)

            pc_data.update({promo_code_name: {"discount_rate": discount_rate, "count": count-1, "type": pc_type}})

        elif pc_type == "service_code":
            if service is None:
                return await ctx.send("Для промокода типа \"`service_code`\" параметр \"`service`\" - обязателен!", ephemeral=True)

            pc_data.update({promo_code_name: {"service": service, "type": pc_type}})

        if date is not None:
            pc_data[promo_code_name].update({"time": date.replace(" ", "")})
        if count_for_use is not None:
            pc_data[promo_code_name].update({"count_for_use": count_for_use})

        await utils.write_json(path=SSBot.PATH_TO_PROMO_CODES_DATA, data=pc_data)

        embed = utils.create_embed(title="Промокод добавлен", color=disnake.Color.blurple(), content=f"Промокод **{promo_code_name}** добавлен в базу данных в категорию \"{pc_type}\".\nКод: ```{pc_data[promo_code_name]}```")

        await ctx.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="remove_promo_code")
    async def remove_promo_code(self, ctx, promo_code_name: str):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        pc_data = await utils.async_read_json(path=SSBot.PATH_TO_PROMO_CODES_DATA)
        pc_data.pop(promo_code_name)
        await utils.write_json(path=SSBot.PATH_TO_PROMO_CODES_DATA, data=pc_data)

        embed = utils.create_embed(title="Промокод удален", color=disnake.Color.red(), content=f"Промокод {promo_code_name} удален из базы данных.")

        await ctx.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="stop_take_order")
    async def stop_take_order(self, ctx, true_or_false: bool = commands.Param(choices=bot_choices.CHOICE_FOR_SURE)):
        if ctx.author.name != SSBot.BOT_DATA["owner_name"] and ctx.author.id != SSBot.BOT_DATA["owner_id"]:
            return await ctx.send(embed=template_embeds.DOESNT_HAVE_PERMISSION, ephemeral=True)

        SSBot.BOT_CONFIG["bot_can_take_order"] = true_or_false

        color = None
        if true_or_false is True:
            color = disnake.Color.blurple()
        elif true_or_false is False:
            color = disnake.Color.red()

        embed = utils.create_embed(title="bot_can_take_order изменен", color=color, content=f"`bot_can_take_order` изменен на `{true_or_false}`.")

        await ctx.send(embed=embed, ephemeral=True)

    # @commands.slash_command(name="test")
    # async def test(self, ctx):
    #     await ctx.send("FSDFSDFSS", view=MemberSelectMenuView(self.client))


def setup(client):
    client.add_cog(OwnerCommands(client))
