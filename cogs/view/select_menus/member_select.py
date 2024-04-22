from disnake import MessageInteraction, Embed, Member
from disnake.ext.commands import Cog, Bot
from disnake.ui import View, UserSelect

from main import SSBot
from cogs.hadlers import utils


class MemberSelectMenuReg(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        print("MemberSelectMenu was added")
        self.bot.add_view(MemberSelectMenuView(bot=self.bot))


class MemberSelectMenu(UserSelect):

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(
            placeholder="Выберите пользователя",
            custom_id="member_select_menu",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: MessageInteraction) -> None:
        avatar: Member.avatar = await utils.get_avatar(self.values[0].avatar)

        user_card: Embed = Embed(title=f"{self.values[0].display_name} // {self.values[0].name}", color=SSBot.DEFAULT_COLOR)
        user_card.add_field(name=f"Статус: {self.values[0].status}\nЗарегистрирован с: {self.values[0].created_at.strftime('%d.%m.%Y %H:%M')} (UTC)\nID: {self.values[0].id}", value="")
        user_card.set_thumbnail(avatar)

        await interaction.send(embed=user_card)


class MemberSelectMenuView(View):

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(MemberSelectMenu(self.bot))


def setup(bot) -> None:
    bot.add_cog(MemberSelectMenuReg(bot))
