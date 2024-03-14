import disnake

from disnake.ext import commands

from ssbot import SSBot
from cogs.hadlers.embeds import support_question_embeds
from cogs.view.buttons.contact_here_button import ContactHereButton


class QuestionSelectReg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("QuestionSelect was added")
        self.bot.add_view(QuestionSelectView(bot=self.bot))


class QuestionSelect(disnake.ui.StringSelect):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(
            placeholder="Какой у вас вопрос?", min_values=1, max_values=1,
            custom_id="question_select", options=[
                disnake.SelectOption(label="Обратная связь", value="connection"),
                disnake.SelectOption(label="Как оформить заказ?", value="how_order"),
                # disnake.SelectOption(label="Как устроена оплата?", value="how_pay"),
                disnake.SelectOption(label="Правки", value="edits"),
                disnake.SelectOption(label="Доп. контакты связи", value="add_contacts"),
                disnake.SelectOption(label="Бот выдает ошибку взаимодействия", value="bot_error"),
                # disnake.SelectOption(label="Как пользоваться архивом?", value="archive"),
                disnake.SelectOption(label="Как стать сотрудником SkylightServices?", value="ss_worker")
            ]
        )

    async def callback(self, ctx):
        embed, flag = None, True

        match self.values[0]:  # проверка `value` выбранной темы и вывод ответа
            case "how_order":
                embed = support_question_embeds.HOW_ORDER_EMBED

            case "edits":
                embed = support_question_embeds.EDITS_EMBED

            case "bot_error":
                flag = False
                embed = support_question_embeds.BOT_ERROR_EMBED

                await ctx.send(embed=embed, file=support_question_embeds.BOT_ERROR_IMG, ephemeral=True)

            case "add_contacts":
                flag = False
                embed = support_question_embeds.ADD_CONTACTS_EMBED

                await ctx.send(embed=embed, file=support_question_embeds.ADD_CONTACTS_MENU_IMG, ephemeral=True)

            case "archive":
                embed = support_question_embeds.ARCHIVE_EMBED

            case "connection":
                flag = False
                embed = support_question_embeds.CONNECTION_EMBED

                await ctx.send(embed=embed, view=ContactHereButton(self.bot), ephemeral=True)

            case "ss_worker":
                embed = support_question_embeds.SS_WORKER

            # case "how_pay":
            #     embed = support_question_embeds.HOW_PAY

        if flag:
            await ctx.send(embed=embed, ephemeral=True)


class QuestionSelectView(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(QuestionSelect(self.bot))


def setup(bot):
    bot.add_cog(QuestionSelectReg(bot))
