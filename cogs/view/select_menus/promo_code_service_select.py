from disnake import Embed, MessageInteraction, SelectOption
from disnake.ext.commands import Cog, Bot
from disnake.ui import View, StringSelect

from main import SSBot
from cogs.hadlers import utils
from cogs.hadlers.dicts import SERVICE_PRICES, NOT_STATIC_PRICE
from cogs.view.buttons.donation_and_promo_code_buttons import DonationAndPromoCodeButtons


class PromoCodeServiceSelectReg(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("PromoCodeServiceSelect was added")
        self.bot.add_view(PromoCodeServiceSelectView(bot=self.bot))


class PromoCodeServiceSelect(StringSelect):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(
            placeholder="Список услуг", min_values=1, max_values=1,
            custom_id="service_select", options=[
                SelectOption(label=SSBot.SERVICES_NAME["skin64"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["skin64"]["code"]]}₽', value="skin64", emoji="🧍‍♂️"),
                SelectOption(label=SSBot.SERVICES_NAME["rew_skin"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["rew_skin"]["code"]]}₽', value="rew_skin", emoji="🧍‍♂️"),

                SelectOption(label=SSBot.SERVICES_NAME["model"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["model"]["code"]]}₽', value="model", emoji="\N{SNOWMAN}"),
                SelectOption(label=SSBot.SERVICES_NAME["anim_model"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["anim_model"]["code"]]}₽', value="anim_model", emoji="\N{SNOWMAN}"),
                SelectOption(label=SSBot.SERVICES_NAME["texture_model"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["texture_model"]["code"]]}₽', value="texture_model", emoji="\N{SNOWMAN}"),

                SelectOption(label=SSBot.SERVICES_NAME["cape"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["cape"]["code"]]}₽', value="cape", emoji="🧶"),
                SelectOption(label=SSBot.SERVICES_NAME["totem"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["totem"]["code"]]}₽', value="totem", emoji="🧶"),
                SelectOption(label=SSBot.SERVICES_NAME["texture"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["texture"]["code"]]}₽', value="texture", emoji="🧶"),

                SelectOption(label=SSBot.SERVICES_NAME["letter_logo"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["letter_logo"]["code"]]}₽', value="letter_logo", emoji="🆎"),
                SelectOption(label=SSBot.SERVICES_NAME["letter_logo_2"]["name"], description=f'от {NOT_STATIC_PRICE[SSBot.SERVICES_NAME["letter_logo_2"]["code"]]}₽', value="letter_logo_2", emoji="🆎"),

                SelectOption(label=SSBot.SERVICES_NAME["characters_design"]["name"], description=f'{SERVICE_PRICES[SSBot.SERVICES_NAME["characters_design"]["code"]]}₽', value="characters_design", emoji="🥚"),
            ]
        )

    async def callback(self, interaction: MessageInteraction) -> None:
        embed: Embed = Embed(title="Проверка", color=SSBot.DEFAULT_COLOR)
        embed.add_field(
            name=f'Вы выбрали услугу ***{await utils.convert_value_to_service_name(value=self.values[0])}***. Если вы по ошибке выбрали не ту услугу, то снова откройте список и выберите нужную вам, иначе продолжите.',
            value='', inline=False
        )

        SSBot.CLIENT_DB_CURSOR.execute(
            "INSERT INTO settings (user_id, service_for_gift) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET service_for_gift=?",
            (interaction.author.id, self.values[0], self.values[0])
        )
        SSBot.CLIENT_DB_CONNECTION.commit()

        await interaction.send(embed=embed, view=DonationAndPromoCodeButtons(self.bot))


class PromoCodeServiceSelectView(View):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(PromoCodeServiceSelect(self.bot))


def setup(bot):
    bot.add_cog(PromoCodeServiceSelectReg(bot))
