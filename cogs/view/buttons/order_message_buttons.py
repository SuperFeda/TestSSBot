import disnake

from disnake.ext.commands import Cog, Bot

from main import BOT, SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds import template_embeds, ordering_embeds
from cogs.view.select_menus.service_select import ServiceSelectView
from cogs.systems.rate_system.stars_button import StarsButton


class OrderMessageButtonsReg(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("OrderMessageButtons was added")
        self.bot.add_view(OrderMessageButtons(bot=self.bot))


class OrderMessageButtons(disnake.ui.View):

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.support_button = disnake.ui.Button(label="Поддержать", url="https://www.donationalerts.com/r/skylightproduction", row=1)
        self.add_item(self.support_button)

    @disnake.ui.button(label="Оформить заказ", style=disnake.ButtonStyle.blurple, custom_id="order_button", row=0)
    async def order_button(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        if SSBot.BOT_CONFIG["bot_can_take_order"] is False:
            return await ctx.send("Процесс оформления заказов временно приостановлен.", ephemeral=True)

        member: disnake.User = BOT.get_user(ctx.author.id)
        owner: disnake.User = BOT.get_user(SSBot.BOT_DATA["owner_id"])
        owner_avatar: disnake.User.avatar = await utils.get_avatar(owner.avatar)
        file: disnake.File = disnake.File("images/SkylightServices_new.png", filename="ss_logo.jpg")

        order_embed: disnake.Embed = disnake.Embed(title="Выбор услуги", color=disnake.Color.blurple())
        order_embed.add_field(name="Выберите желаемую услугу из списка ниже:", value="")
        order_embed.set_image(url="attachment://ss_logo.jpg")
        order_embed.set_footer(
            text=f"{owner.display_name}: Вы автоматически соглашаетесь с пользовательским соглашением после оформления заказа",
            icon_url=owner_avatar
        )

        try:
            await member.send(f"<@{ctx.author.id}>", embed=order_embed, file=file, view=ServiceSelectView(self.bot))
            await ctx.send(embed=template_embeds.CONTINUE_ORDERING, ephemeral=True)
        except disnake.errors.Forbidden:
            await ctx.send(embed=ordering_embeds.WARN_PM_IS_OFF, ephemeral=True)

    @disnake.ui.button(label="Отзывы", style=disnake.ButtonStyle.green, custom_id="reviews_button", row=0)
    async def reviews_button(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await ctx.send(embed=template_embeds.FEEDBACK_EMBED, ephemeral=True)

    @disnake.ui.button(label="Оставить отзыв", style=disnake.ButtonStyle.green, custom_id="leave_review_button", row=0)
    async def leave_review_button(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        thread: disnake.Thread = await ctx.channel.create_thread(
            name=f"{ctx.author.name}'s отзыв",
            type=disnake.ChannelType.private_thread
        )

        embed: disnake.Embed = utils.create_embed(
            title="Продолжение создания",
            color=SSBot.DEFAULT_COLOR,
            content=f"Для того чтобы продолжить создание отзыва перейдите в ветку <#{thread.id}>"
        )

        await ctx.send(embed=embed, ephemeral=True)
        await thread.send(f'<@{ctx.author.id}>', embed=template_embeds.START_CREATING_REVIEW_EMBED, view=StarsButton(self.bot))

    @disnake.ui.button(label="Пользовательское соглашение", style=disnake.ButtonStyle.gray, custom_id="ps_button", row=1)
    async def ps_button(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await ctx.send(embed=template_embeds.PS_EMBED, ephemeral=True)

    @disnake.ui.button(label="Доп. примеры работ", style=disnake.ButtonStyle.gray, custom_id="work_examples_button", row=1)
    async def work_examples_button(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await ctx.send(embed=template_embeds.ADDITIONAL_WORK_EXAMPLES, ephemeral=True)

    def to_components(self):
        return super().to_components()


def setup(bot):
    bot.add_cog(OrderMessageButtonsReg(bot))
