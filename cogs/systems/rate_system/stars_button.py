import disnake, sqlite3

from disnake.ext import commands

from ssbot import SSBot, BOT
from cogs.hadlers import utils
from cogs.view.buttons.enter_description_button import EnterDescriptionButton


class StarsButtonButtonReg(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("StarsButton was added")
        self.client.add_view(StarsButton(bot=self.client))


class StarsButton(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="🌟", style=disnake.ButtonStyle.red, custom_id="one_star_button")
    async def one_star(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await self.star_select_output(ctx=interaction, star_count=1)

    @disnake.ui.button(label="🌟🌟", style=disnake.ButtonStyle.grey, custom_id="two_star_button")
    async def two_star(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await self.star_select_output(ctx=interaction, star_count=2)

    @disnake.ui.button(label="🌟🌟🌟", style=disnake.ButtonStyle.grey, custom_id="three_star_button")
    async def three_star(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await self.star_select_output(ctx=interaction, star_count=3)

    @disnake.ui.button(label="🌟🌟🌟🌟", style=disnake.ButtonStyle.green, custom_id="four_star_button")
    async def four_star(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await self.star_select_output(ctx=interaction, star_count=4)

    @disnake.ui.button(label="🌟🌟🌟🌟🌟", style=disnake.ButtonStyle.green, custom_id="five_star_button")
    async def five_star(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await self.star_select_output(ctx=interaction, star_count=5)

    async def star_select_output(self, ctx, star_count: int) -> None:
        """
        Вывод после выбора оценки по 5 бальной шкале
        :param ctx: ctx
        :param star_count: кол-во звезд
        :return: None
        """
        connection_ = sqlite3.connect(SSBot.PATH_TO_CLIENT_DB)
        cursor_ = connection_.cursor()
        cursor_.execute(
            "INSERT INTO settings (user_id, stars) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET stars=?",
            (ctx.author.id, star_count, star_count)
        )
        connection_.commit()
        connection_.close()

        embed = utils.create_embed(title="Ввод описания и проверка", color=SSBot.DEFAULT_COLOR, content=f"Вы выбрали {await utils.star_count_conv(star_count)}, если вы выбрали не ту оценку, то выберете её еще раз ниже:\n\nВ случае, если оценка выбрана верно, начните заполнять текст вашего отзыва нажав на кнопку \"Ввод описания\".")

        components_list = [
            StarsButton(self.bot).one_star,
            StarsButton(self.bot).two_star,
            StarsButton(self.bot).three_star,
            StarsButton(self.bot).four_star,
            StarsButton(self.bot).five_star,
            EnterDescriptionButton(self.bot).enter_desc_button
        ]

        await ctx.send(embed=embed, components=components_list)


def setup(client):
    client.add_cog(StarsButtonButtonReg(client))
