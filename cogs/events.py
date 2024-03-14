import disnake, sqlite3, os

from disnake.ext import commands
from colorama import Fore

from ssbot import BOT, SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds import ordering_embeds, template_embeds, support_question_embeds
from cogs.view.select_menus.question_select import QuestionSelectView
from cogs.view.buttons.order_message_buttons import OrderMessageButtons
from cogs.view.buttons.continue_and_adtcon_buttons import ContinueAndAdtConButtons
from cogs.view.buttons.write_description_again_button import EnterDescriptionAgainButton
from cogs.systems.rate_system.continue_button_for_review import ContinueButtonForReview


class BotEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        # отправка сообщения, через которое происходит оформление заказа в канал ORDER_CHANNEL, как только бот становится активен
        print(f"{Fore.RED}[WARN]{Fore.RESET} Бот запущен и готов начать самую большую оргию")

        ORDER_CHANNEL = BOT.get_channel(SSBot.BOT_CONFIG["order_channel_id"])
        SUPPORT_CHANNEL = BOT.get_channel(SSBot.BOT_CONFIG["support_channel_id"])

        await SUPPORT_CHANNEL.send(embed=support_question_embeds.SUPPORT_EMBED, view=QuestionSelectView(self.client))
        await ORDER_CHANNEL.send(embed=ordering_embeds.START_ORDERING_EMBED, file=ordering_embeds.SS_LOGO, view=OrderMessageButtons(self.client))

    @commands.Cog.listener()
    async def on_message(self, message):
        connection = sqlite3.connect(SSBot.PATH_TO_CLIENT_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT can_description FROM settings WHERE user_id=?", (message.author.id,))
        result = cursor.fetchone()
        can_description_var = result[0] if result else None
        connection.close()

        if message.channel.type is disnake.ChannelType.private_thread and message.author.name in message.channel.name:
            def is_not_bot(m):
                return not m.author.bot

            await message.channel.purge(check=is_not_bot)  # Удаление сообщений в новосозданной ветке

        if can_description_var == 1 or can_description_var is True:
            if isinstance(message.channel, disnake.DMChannel):
                await self.order_path(message=message)
            try:
                await self.review_path(message=message)
            except AttributeError:
                pass

        LOG_CHANNEL = BOT.get_channel(SSBot.BOT_CONFIG["log_channel_id"])

        if message.author != BOT.user:                                        # отправка сообщений от всех пользователей в LOG_CHANNEL, если id канала, где
            if message.channel.id in SSBot.BOT_CONFIG["banned_channels_id"]:  # было опубликованно сообщение не находится в banned_channels и автор сообщения не SSBot
                return
            avatar = await utils.get_avatar(ctx_user_avatar=message.author.avatar)

            embed = disnake.Embed(title="Сообщение", color=SSBot.DEFAULT_COLOR)
            embed.add_field(name=f'"<#{message.channel.id}>" :>> ', value=message.content)
            embed.set_author(name=message.author.display_name, icon_url=avatar)
            try:
                await LOG_CHANNEL.send(embed=embed)
            except disnake.errors.HTTPException:
                await LOG_CHANNEL.send(f"В <#{message.channel.id}> было отправлено сообщение длинной больше 1024 символов от {message.author.display_name} ({message.author.name})")

        await BOT.process_commands(message)

    def load_can_description_var(self, user_id) -> None:
        connection_ = sqlite3.connect(SSBot.PATH_TO_CLIENT_DB)
        cursor_ = connection_.cursor()
        cursor_.execute(
            "INSERT INTO settings (user_id, can_description) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET can_description=?",
            (user_id, False, False)
        )
        connection_.commit()
        connection_.close()

    async def order_path(self, message) -> None | disnake.Message:
        len_message_content = len(message.content)
        len_message_attachments = len(message.attachments)

        if len_message_attachments > 10:
            self.load_can_description_var(user_id=message.author.id)
            return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=template_embeds.WARN_MANY_IMAGES_EMBED)
        if len_message_content > 1020:
            self.load_can_description_var(user_id=message.author.id)
            return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=template_embeds.WARN_LONG_DESC_EMBED)
        if len_message_content < 10:
            self.load_can_description_var(user_id=message.author.id)
            return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=template_embeds.WARN_SHORT_DESC_EMBED)

        pictures = None
        embed_for_send = []

        connection_ = sqlite3.connect(SSBot.PATH_TO_CLIENT_DB)
        cursor_ = connection_.cursor()
        cursor_.execute(
            "INSERT INTO settings (user_id, service_description) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET service_description=?",
            (message.author.id, message.content, message.content)
        )
        connection_.commit()
        connection_.close()

        async with message.channel.typing():
            if message.author.name in os.listdir("cache/"):  # если папка с именем пользователя уже есть в папке с кешем, то удалить ее и ее содержимое
                await utils.delete_files_from_cache(author_name=message.author.name)

            desc = disnake.Embed(title="Проверка описания", color=SSBot.DEFAULT_COLOR)
            desc.add_field(
                name=f"Проверьте введенное вами описание и прикрепленные фотографии (при наличии):",
                value=f"**{message.content}**", inline=False
            )
            desc.add_field(
                name="При наличиии ошибок в тексте или если забыли что-то дописать, то нажмите на кнопку \"Ввести повторно\".\n\nЕсли вы можете предоставить дополнительные контакты для связи, то нажмите на кнопку \"Доп. контакты\"",
                value="", inline=False
            )
            embed_for_send.append(desc)

            if len_message_attachments > 0:
                banned_filenames = []
                for image in message.attachments:
                    img_fln = image.filename[-5:]
                    # если файл имеет не разрешенный формат, то добавить его имя в список "banned_filenames"
                    if ".png" not in img_fln and ".jpeg" not in img_fln and ".gif" not in img_fln and ".jpg" not in img_fln:
                        banned_filenames.append(image.filename)
                    else:
                        try:
                            os.mkdir(f"cache/{message.author.name}/")  # создание папки с именем пользователя в кеше
                        except FileExistsError:
                            pass

                        await image.save(f"cache/{message.author.name}/{image.filename}")

                if banned_filenames:
                    banned_files_embed = disnake.Embed(
                        title="Файлы заблокированы", color=disnake.Color.red(),
                        description="**Список заблокированных файлов из-за не поддерживаемого формата:** {}".format(", ".join(banned_filenames))
                    )
                    embed_for_send.append(banned_files_embed)

                embed_for_send.append(ordering_embeds.WARNING_MESSAGE_EMBED)

                try:
                    pictures = await utils.get_files_disnake(f"cache/{message.author.name}/")  # получение сохраненных фотографий из кеша
                except FileNotFoundError:
                    pass

        self.load_can_description_var(user_id=message.author.id)

        components_list = [
            EnterDescriptionAgainButton(self.client).enter_desc_button,
            ContinueAndAdtConButtons(self.client).continue_button,
            ContinueAndAdtConButtons(self.client).additional_contacts_button
        ]

        await message.channel.send(embeds=embed_for_send, files=pictures, components=components_list)

    async def review_path(self, message) -> None | disnake.Message:
        if "отзыв" in message.channel.name:
            len_message_content = len(message.content)
            len_message_attachments = len(message.attachments)

            if len_message_attachments > 1:
                self.load_can_description_var(user_id=message.author.id)
                return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=template_embeds.WARN_MANY_IMAGES_FOR_REVIEW_EMBED)
            if len_message_content > 1020:
                self.load_can_description_var(user_id=message.author.id)
                return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=template_embeds.WARN_LONG_DESC_EMBED)
            if len_message_content < 10:
                self.load_can_description_var(user_id=message.author.id)
                return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=template_embeds.WARN_SHORT_DESC_EMBED)
            if len_message_attachments > 0:
                img_fln = message.attachments[0].filename[-5:]
                if ".png" not in img_fln and ".jpeg" not in img_fln and ".gif" not in img_fln and ".jpg" not in img_fln:
                    self.load_can_description_var(user_id=message.author.id)
                    return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=template_embeds.BANNED_FILE_EMBED)

            picture = None

            connection_ = sqlite3.connect(SSBot.PATH_TO_CLIENT_DB)
            cursor_ = connection_.cursor()
            cursor_.execute(
                "INSERT INTO settings (user_id, service_description) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET service_description=?",
                (message.author.id, message.content, message.content)
            )
            connection_.commit()
            connection_.close()

            async with message.channel.typing():
                if message.author.name in os.listdir("cache/"):  # если папка с именем пользователя уже есть в папке с кешем, то удалить ее и ее содержимое
                    await utils.delete_files_from_cache(author_name=message.author.name)

                desc = disnake.Embed(title="Проверка описания", color=SSBot.DEFAULT_COLOR)
                desc.add_field(
                    name=f"Проверьте введенное вами описание и прикрепленные фотографии (при наличии):",
                    value=f"**{message.content}**", inline=False
                )
                desc.add_field(
                    name="При наличиии ошибок в тексте или если забыли что-то дописать, то нажмите на кнопку \"Ввести повторно\".",
                    value="", inline=False
                )

                if len_message_attachments > 0:
                    for image in message.attachments:
                        try:
                            os.mkdir(f"cache/{message.author.name}/")  # создание папки с именем пользователя в кеше
                        except FileExistsError:
                            pass

                        await image.save(f"cache/{message.author.name}/{image.filename}")

                try:
                    picture = await utils.get_files(f"cache/{message.author.name}/")  # получение сохраненных фотографий из кеша
                    picture = disnake.File(picture[0], filename="image_for_review.jpg")
                    desc.set_image(url="attachment://image_for_review.jpg")
                except FileNotFoundError:
                    pass

            self.load_can_description_var(user_id=message.author.id)

            components_list = [
                EnterDescriptionAgainButton(self.client).enter_desc_button,
                ContinueButtonForReview(self.client).continue_button_for_review
            ]

            await message.channel.send(embed=desc, file=picture, components=components_list)


def setup(client):
    client.add_cog(BotEvents(client))
