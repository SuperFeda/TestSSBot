from disnake import DMChannel, ChannelType, errors, Embed, Color, File, Message
from disnake.ext import commands
from os import listdir, mkdir
from colorama import Fore

from main import BOT, SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds.template_embeds import WARN_MANY_IMAGES_EMBED, WARN_LONG_DESC_EMBED, WARN_SHORT_DESC_EMBED, BANNED_FILE_EMBED, WARN_MANY_IMAGES_FOR_REVIEW_EMBED
from cogs.hadlers.embeds.ordering_embeds import START_ORDERING_EMBED, SS_LOGO, WARNING_MESSAGE_EMBED
from cogs.hadlers.embeds.support_question_embeds import SUPPORT_EMBED
from cogs.view.select_menus.question_select import QuestionSelectView
from cogs.view.buttons.order_message_buttons import OrderMessageButtons
from cogs.view.buttons.service_promo_code_button import ServicePromoCodeButton
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

        ORDER_CHANNEL = BOT.get_channel(SSBot.BOT_DATA["order_channel_id"])
        SUPPORT_CHANNEL = BOT.get_channel(SSBot.BOT_DATA["support_channel_id"])

        components = [
            OrderMessageButtons(self.client).order_button,
            ServicePromoCodeButton(self.client).promo_code_button,
            OrderMessageButtons(self.client).reviews_button,
            OrderMessageButtons(self.client).leave_review_button,
            OrderMessageButtons(self.client).support_button,
            OrderMessageButtons(self.client).ps_button,
            OrderMessageButtons(self.client).work_examples_button
        ]

        await SUPPORT_CHANNEL.send(embed=SUPPORT_EMBED, view=QuestionSelectView(self.client))
        await ORDER_CHANNEL.send(embed=START_ORDERING_EMBED, file=SS_LOGO, components=components)

    # @commands.Cog.listener()
    # async def on_member_join(self, message):
    #     embed = disnake.Embed(title="Новый участник!", color=SSBot.DEFAULT_COLOR)
    #     embed.add_field(name="", value="")
    #     embed.set_author(name=f"{message.author.display_name} // {message.author.name}", icon_url=await utils.get_avatar(ctx_user_avatar=message.author.avatar))

    @commands.Cog.listener()
    async def on_message(self, message):
        SSBot.CLIENT_DB_CURSOR.execute("SELECT can_description FROM settings WHERE user_id=?", (message.author.id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        can_description_var = result[0] if result else None

        if message.channel.type is ChannelType.private_thread and message.author.name in message.channel.name:
            def is_not_bot(m):
                return not m.author.bot

            await message.channel.purge(check=is_not_bot)  # Удаление сообщений в новосозданной ветке

        if can_description_var == 1 or can_description_var is True:
            if isinstance(message.channel, DMChannel):
                await self.order_path(message=message)
            try:
                await self.review_path(message=message)
            except AttributeError:
                pass

        LOG_CHANNEL = BOT.get_channel(SSBot.BOT_DATA["log_channel_id"])

        if message.author != BOT.user:                                      # отправка сообщений от всех пользователей в LOG_CHANNEL, если id канала, где
            if message.channel.id in SSBot.BOT_DATA["banned_channels_id"]:  # было опубликованно сообщение не находится в banned_channels и автор сообщения не SSBot
                return
            avatar = await utils.get_avatar(ctx_user_avatar=message.author.avatar)

            embed = Embed(title="Сообщение", color=SSBot.DEFAULT_COLOR)
            embed.add_field(name=f'"<#{message.channel.id}>" :>> ', value=message.content)
            embed.set_author(name=message.author.display_name, icon_url=avatar)
            try:
                await LOG_CHANNEL.send(embed=embed)
            except errors.HTTPException:
                await LOG_CHANNEL.send(f"В <#{message.channel.id}> было отправлено сообщение длинной больше 1024 символов от {message.author.display_name} ({message.author.name})")

        await BOT.process_commands(message)

    def __set_can_description_to_false(self, user_id) -> None:
        SSBot.CLIENT_DB_CURSOR.execute(
            "INSERT INTO settings (user_id, can_description) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET can_description=?",
            (user_id, False, False)
        )
        SSBot.CLIENT_DB_CONNECTION.commit()

    async def order_path(self, message) -> None | Message:
        len_message_content = len(message.content)
        len_message_attachments = len(message.attachments)

        if len_message_attachments > 10:
            self.__set_can_description_to_false(user_id=message.author.id)
            return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=WARN_MANY_IMAGES_EMBED)
        if len_message_content > 1020:
            self.__set_can_description_to_false(user_id=message.author.id)
            return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=WARN_LONG_DESC_EMBED)
        if len_message_content < 10:
            self.__set_can_description_to_false(user_id=message.author.id)
            return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=WARN_SHORT_DESC_EMBED)

        pictures = None
        embed_for_send = []

        SSBot.CLIENT_DB_CURSOR.execute(
            "INSERT INTO settings (user_id, service_description) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET service_description=?",
            (message.author.id, message.content, message.content)
        )
        SSBot.CLIENT_DB_CONNECTION.commit()

        async with message.channel.typing():
            if message.author.name in listdir("cache/"):  # если папка с именем пользователя уже есть в папке с кешем, то удалить ее и ее содержимое
                await utils.delete_files_from_cache(author_name=message.author.name)

            desc = Embed(title="Проверка описания", color=SSBot.DEFAULT_COLOR)
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
                            mkdir(f"cache/{message.author.name}/")  # создание папки с именем пользователя в кеше
                        except FileExistsError:
                            pass

                        await image.save(f"cache/{message.author.name}/{image.filename}")

                if banned_filenames:
                    banned_files_embed = Embed(
                        title="Файлы заблокированы", color=Color.red(),
                        description="**Список заблокированных файлов из-за не поддерживаемого формата:** {}".format(", ".join(banned_filenames))
                    )
                    embed_for_send.append(banned_files_embed)

                embed_for_send.append(WARNING_MESSAGE_EMBED)

                try:
                    pictures = await utils.get_files_disnake(f"cache/{message.author.name}/")  # получение сохраненных фотографий из кеша
                except FileNotFoundError:
                    pass

        self.__set_can_description_to_false(user_id=message.author.id)

        components_list = [
            EnterDescriptionAgainButton(self.client).enter_desc_button,
            ContinueAndAdtConButtons(self.client).continue_button,
            ContinueAndAdtConButtons(self.client).additional_contacts_button
        ]

        await message.channel.send(embeds=embed_for_send, files=pictures, components=components_list)

    async def review_path(self, message) -> None | Message:
        if "отзыв" in message.channel.name:
            len_message_content = len(message.content)
            len_message_attachments = len(message.attachments)

            if len_message_attachments > 1:
                self.__set_can_description_to_false(user_id=message.author.id)
                return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=WARN_MANY_IMAGES_FOR_REVIEW_EMBED)
            if len_message_content > 1020:
                self.__set_can_description_to_false(user_id=message.author.id)
                return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=WARN_LONG_DESC_EMBED)
            if len_message_content < 10:
                self.__set_can_description_to_false(user_id=message.author.id)
                return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=WARN_SHORT_DESC_EMBED)
            if len_message_attachments > 0:
                img_fln = message.attachments[0].filename[-5:]
                if ".png" not in img_fln and ".jpeg" not in img_fln and ".gif" not in img_fln and ".jpg" not in img_fln:
                    self.__set_can_description_to_false(user_id=message.author.id)
                    return await message.channel.send(f"<@{message.author.id}>", view=EnterDescriptionAgainButton(self.client), embed=BANNED_FILE_EMBED)

            picture = None

            SSBot.CLIENT_DB_CURSOR.execute(
                "INSERT INTO settings (user_id, service_description) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET service_description=?",
                (message.author.id, message.content, message.content)
            )
            SSBot.CLIENT_DB_CONNECTION.commit()

            async with message.channel.typing():
                if message.author.name in listdir("cache/"):  # если папка с именем пользователя уже есть в папке с кешем, то удалить ее и ее содержимое
                    await utils.delete_files_from_cache(author_name=message.author.name)

                desc = Embed(title="Проверка описания", color=SSBot.DEFAULT_COLOR)
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
                            mkdir(f"cache/{message.author.name}/")  # создание папки с именем пользователя в кеше
                        except FileExistsError:
                            pass

                        await image.save(f"cache/{message.author.name}/{image.filename}")

                try:
                    picture = await utils.get_files(f"cache/{message.author.name}/")  # получение сохраненных фотографий из кеша
                    picture = File(picture[0], filename="image_for_review.jpg")
                    desc.set_image(url="attachment://image_for_review.jpg")
                except FileNotFoundError:
                    pass

            self.__set_can_description_to_false(user_id=message.author.id)

            components_list = [
                EnterDescriptionAgainButton(self.client).enter_desc_button,
                ContinueButtonForReview(self.client).continue_button_for_review
            ]

            await message.channel.send(embed=desc, file=picture, components=components_list)


def setup(client):
    client.add_cog(BotEvents(client))
