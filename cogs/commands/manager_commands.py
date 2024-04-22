import disnake

from disnake.ext.commands import Cog, slash_command, Context

from main import SSBot, BOT
from cogs.hadlers import dicts
from cogs.hadlers.embeds.template_embeds import DOESNT_HAVE_PERMISSION
from cogs.hadlers.embeds.ordering_embeds import START_ORDERING_EMBED
from cogs.hadlers.embeds.support_question_embeds import SUPPORT_EMBED
from cogs.view.buttons.order_message_buttons import OrderMessageButtons
from cogs.view.select_menus.question_select import QuestionSelectView


class ManagerCommands(Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="summon_order_panel")
    async def summon_order_panel(self, ctx):
        if disnake.utils.get(ctx.guild.roles, id=SSBot.BOT_DATA["manager_role_id"]) not in ctx.author.roles:
            return await ctx.send(embed=DOESNT_HAVE_PERMISSION, ephemeral=True)

        ORDER_CHANNEL: disnake.TextChannel = BOT.get_channel(SSBot.BOT_DATA["order_channel_id"])

        # order_embed = disnake.Embed(title="Здароу, я SkylightBot", color=disnake.Color.blurple())
        # order_embed.add_field(name="С моей помощью вы сможете полностью оформить заказ: выбор услуги и создание описания - со всем этим буду помогать я.\nДля начала заполнения нажмите на кнопку \"Оформить заказ\".", value="")

        await ORDER_CHANNEL.send(embed=START_ORDERING_EMBED, view=OrderMessageButtons(self.bot))

    @slash_command(name="summon_support_panel")
    async def summon_support_panel(self, ctx):
        if disnake.utils.get(ctx.guild.roles, id=SSBot.BOT_DATA["manager_role_id"]) not in ctx.author.roles:
            return await ctx.send(embed=DOESNT_HAVE_PERMISSION, ephemeral=True)

        SUPPORT_CHANNEL: disnake.TextChannel = BOT.get_channel(SSBot.BOT_DATA["support_channel_id"])

        # support_embed = disnake.Embed(title="Поддержка", color=disnake.Color.blurple())
        # support_embed.add_field(name="Тут я могу ответить на все вопросы, которые могли появится у вас во время работы с сервисом.\nВыберите интересующую вас тему в списке ниже:", value="")

        await SUPPORT_CHANNEL.send(embed=SUPPORT_EMBED, view=QuestionSelectView(self.bot))

    # @commands.slash_command(name="clear_services_list")
    # async def clear_services_list(self, ctx):
    #     if disnake.utils.get(ctx.guild.roles, id=SSBot.BOT_DATA["manager_role_id"]) not in ctx.author.roles:
    #         embed = utils.create_embed(title="Не достаточно прав", color=disnake.Color.red(),  content="У вас нет прав на использование этой команды.")
    #         return await ctx.send(embed=embed, ephemeral=True)
    #
    #     SERVICES_CHANNEL = BOT.get_channel(1211977678023036958)

    @slash_command(name="update_services_list")
    async def update_services_list(self, ctx):
        if disnake.utils.get(ctx.guild.roles, id=SSBot.BOT_DATA["manager_role_id"]) not in ctx.author.roles:
            return await ctx.send(embed=DOESNT_HAVE_PERMISSION, ephemeral=True)

        await ctx.response.defer(ephemeral=True)

        SERVICES_CHANNEL: disnake.ForumChannel = BOT.get_channel(SSBot.BOT_DATA["services_channel_id"])

        # Создание страницы с услугой "Плащ"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Плащ",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Скин")],
            icon_path="images/services_icons/cape_icon.jpg",
            icon_name="cape_icon.jpg",
            embed_title="Плащ",
            embed_field_name=f'Цена: {dicts.SERVICE_PRICES[SSBot.SERVICES_NAME["cape"]["code"]]}₽\n\nИнтересный вариант для того, чтобы разнообразить ваш скин.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/cape_example.jpg")]
        )

        # Создание страницы с услугой "Текстура для блока/предмета"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Текстура для блока/предмета",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Текстура")],
            icon_path="images/services_icons/texture_icon.png",
            icon_name="texture_icon.jpg",
            embed_title="Текстура для блока/предмета",
            embed_field_name=f'Цена: {dicts.SERVICE_PRICES[SSBot.SERVICES_NAME["texture"]["code"]]}₽\n\nТекстура - основное составляющее всего визуала Minecraft. Мы реализуем любые идеи для модов, ресурс-паков и не только, для улучшения того самого визуала.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/texture_example.png"), disnake.File("images/services_work_examples/texture_example_2.jpg"), disnake.File("images/services_work_examples/texture_example_3.png")]
        )

        # Создание страницы с услугой "Промокод на услугу"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Промокод на услугу",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Специально")],
            icon_path="images/services_icons/promo_code_icon.png",
            icon_name="promo_code_icon.jpg",
            embed_title="Промокод на услугу",
            embed_field_name=f'Цена: *зависит от выбранной для дарения услуги*\n\nПорадуйте знакомого подарочным промокодом на любую услугу в SkylightServices!\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:'
        )

        # Создание страницы с услугой "Дизайн персонажей"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Дизайн персонажей",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Специально")],
            icon_path="images/services_icons/characters_design_icon.png",
            icon_name="characters_design_icon.jpg",
            embed_title="Дизайн персонажей",
            embed_field_name=f'Цена: {dicts.SERVICE_PRICES[SSBot.SERVICES_NAME["characters_design"]["code"]]}₽\n\nРисовка персонажей в уникальном стиле, которых можно использовать в создании анимации или любых других целей.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/characters_design_example.png"), disnake.File("images/services_work_examples/characters_design_example_2.png")]
        )

        # Создание страницы с услугой "Тотем"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Тотем",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Текстура")],
            icon_path="images/services_icons/totem_icon.png",
            icon_name="totem_icon.jpg",
            embed_title="Тотем",
            embed_field_name=f'Цена: {dicts.SERVICE_PRICES[SSBot.SERVICES_NAME["totem"]["code"]]}₽\n\nХотите ли вы, чтобы тотем сохраняющий вашу жизнь, был похож на вас или вашего товарища? Тогда мы поможем в реализации вашей идеи!\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/totem_example.png"), disnake.File("images/services_work_examples/totem_example_2.png")]
        )

        # Создание страницы с услугой "Перерисовка скина"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Перерисовка скина",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Скин")],
            icon_path="images/services_icons/rew_skin_icon.png",
            icon_name='rew_skin_icon.jpg',
            embed_title='Перерисовка скина',
            embed_field_name=f'Цена: {dicts.SERVICE_PRICES[SSBot.SERVICES_NAME["rew_skin"]["code"]]}₽\n\nПерерисовка скина подойдет для тех, кто хочет сохранить образ своего персонажа, но при этом повысить качество.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/rew_skin_example.png")]
        )

        # Создание страницы с услугой "Скин 64х64"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Скин 64х64",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Скин")],
            icon_path="images/services_icons/skin_icon.png",
            icon_name="skin_icon.jpg",
            embed_title="Скин 64х64",
            embed_field_name=f'Цена: {dicts.SERVICE_PRICES[SSBot.SERVICES_NAME["skin64"]["code"]]}₽\n\nНадоели обычные Стив и Алекс? Новые скины тоже успели надоесть? Тогда мы поможем вам создать уникальный дизайн для вашего скина.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/skins_example.png")]
        )

        # Создание страницы с услугой "Модель"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Модель",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Модель")],
            icon_path="images/services_icons/model_icon.jpg",
            icon_name="model_icon.jpg",
            embed_title="Модель",
            embed_field_name=f'**Цена только модели: от {dicts.NOT_STATIC_PRICE[SSBot.SERVICES_NAME["model"]["code"]]}₽**\n**Цена модели + текстура: от {dicts.NOT_STATIC_PRICE[SSBot.SERVICES_NAME["texture_model"]["code"]]}₽**\n**Цена модели + анимация: от {dicts.NOT_STATIC_PRICE[SSBot.SERVICES_NAME["anim_model"]["code"]]}₽**\n\nМодель - один из главных элементов любого мода, способный показать весь визуал модификации.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/model_example.jpg"), disnake.File("images/services_work_examples/model_example_2.png"), disnake.File("images/services_work_examples/model_animation_example.gif")]
        )

        # Создание страницы с услугой "Буквенный логотип"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Буквенный логотип",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Логотип")],
            icon_path="images/services_icons/logo_icon.png",
            icon_name="logo_icon.jpg",
            embed_title="Буквенный логотип",
            embed_field_name=f'Цена: {dicts.SERVICE_PRICES[SSBot.SERVICES_NAME["letter_logo"]["code"]]}₽\n\nОтличная вещь для оформления сервера или страницы скачивания мода.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/logo_example.png")]
        )

        # Создание страницы с услугой "Буквенный логотип с кастомными буквами/доп. деталями"
        await self.create_service_page(
            service_channel=SERVICES_CHANNEL,
            thread_name="Буквенный логотип с кастомными буквами/доп. деталями",
            tags=[SERVICES_CHANNEL.get_tag_by_name("Логотип")],
            icon_path="images/services_icons/logo2_icon.png",
            icon_name="logo2_icon.jpg",
            embed_title="Буквенный логотип с кастомными буквами/доп. деталями",
            embed_field_name=f'Цена: от {dicts.NOT_STATIC_PRICE[SSBot.SERVICES_NAME["letter_logo_2"]["code"]]}₽\n\nОтличная вещь для оформления сервера или страницы скачивания мода.\n\n(Оформить заказ можно здесь: <#{SSBot.BOT_DATA["order_channel_id"]}>) ',
            embed_field_value=':arrow_down::arrow_down: ***Примеры работ ниже*** :arrow_down::arrow_down:',
            examples=[disnake.File("images/services_work_examples/logo2_examples.png")]
        )

        await ctx.edit_original_message("Список услуг обновлен.")

    async def create_service_page(self, *,
                                  service_channel: disnake.ForumChannel,
                                  thread_name: str,
                                  icon_path: str,
                                  tags: list[disnake.ForumTag],
                                  icon_name: str,
                                  embed_title: str,
                                  embed_field_name: str,
                                  embed_field_value: str,
                                  examples: list[disnake.File] | None = None,
                                  color: disnake.Color | None = disnake.Color.blurple()
                                  ) -> None:
        """
        Создание страницы с описанием услуги в канале-форуме по определенному шаблону.
        :param service_channel: Канал-форум в котором нужно сделать публикацию.
        :param thread_name: Имя публикации.
        :param icon_path: Путь к иконке услуги.
        :param tags: Теги для публикации. Должны относить услугу к какой-то категории, которую и символизирует тег.
        :param icon_name: Имя для иконки услуги.
        :param embed_title: Заголовок ``Embed``.
        :param embed_field_name: Заполнение параметра ``name`` для ``disnake.Embed.add_field()``.
        :param embed_field_value: Заполнение параметра ``value`` для ``disnake.Embed.add_field()``.
        :param examples: Примеры работ к данной услуге.
        :param color: Цвет боковой полоски ``Embed``.
        :return: None
        """
        icon = disnake.File(icon_path, filename=icon_name)
        embed = disnake.Embed(title=embed_title, color=color)
        embed.add_field(name=embed_field_name, value=embed_field_value, inline=False)
        embed.set_image(url=f"attachment://{icon_name}")

        THREAD_DATA = await service_channel.create_thread(applied_tags=tags, name=thread_name, embed=embed, file=icon)
        THREAD = BOT.get_channel(THREAD_DATA.thread.id)

        if examples is not None:
            await THREAD.send("Примеры работ:", files=examples)


def setup(bot):
    bot.add_cog(ManagerCommands(bot))
