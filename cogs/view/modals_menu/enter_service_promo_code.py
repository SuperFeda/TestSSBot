from disnake import Embed, TextInputStyle, ModalInteraction, Member
from disnake.ui.modal import Modal, TextInput
from disnake.ext.commands import Cog

from main import SSBot
from cogs.hadlers import utils
from cogs.hadlers.embeds import template_embeds
from cogs.view.buttons.continue_cancel_buttons import ContinueAndCancelButtons


class EnterServicePromoCodeMenuReg(Cog):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("EnterServicePromoCodeMenu was added")
        self.bot.add_view(EnterServicePromoCodeMenu(bot=self.bot))


class EnterServicePromoCodeMenu(Modal):

    def __init__(self, bot):
        self.bot = bot
        super().__init__(
            title="Ввод промокода", custom_id="service_promo_code_menu",
            timeout=300.0, components=[
                TextInput(
                    label="Промокод",
                    placeholder="Введите промокод",
                    custom_id="serv_code",
                    required=True,
                    style=TextInputStyle.short,
                    max_length=50,
                )
            ]
        )

    async def callback(self, ctx: ModalInteraction):
        enter_promo_code: str = ctx.text_values["serv_code"]
        promo_codes_data: dict = await utils.async_read_json(SSBot.PATH_TO_PROMO_CODES_DATA)
        member: Member = ctx.guild.get_member(ctx.author.id)

        if enter_promo_code not in promo_codes_data:
            return await ctx.send(embed=template_embeds.WARN_PROMO_CODE_NOT_IN_DB)
        if promo_codes_data[enter_promo_code]["type"] != "service_code":
            return await ctx.send(embed=template_embeds.PROMO_CODE_DAS_NOT_A_GIFT, ephemeral=True)

        SSBot.CLIENT_DB_CURSOR.execute("SELECT activated_promo_codes_list FROM settings WHERE user_id=?", (ctx.author.id,))
        result = SSBot.CLIENT_DB_CURSOR.fetchone()
        activated_promo_codes_list_var = result[0] if result else None

        if activated_promo_codes_list_var is not None:
            user_codes: list = await utils.string_to_list(activated_promo_codes_list_var)

            if enter_promo_code in user_codes:
                return await ctx.send(embed=template_embeds.WARN_PROMO_CODE_WAS_PREVIOUSLY_ENTERED_EMBED, ephemeral=True)

        service: str = await utils.convert_value_to_service_name(promo_codes_data[enter_promo_code]["service"])

        embed: Embed = Embed(title="Промокод активирован!", color=SSBot.DEFAULT_COLOR)
        embed.add_field(
            name=f'Подарочный промокод на услугу ***{service}*** активирован. Выберите дальнейшие действия:',
            value="", inline=False
        )

        await member.send(embed=embed, view=ContinueAndCancelButtons(bot=self.bot, promo_code=enter_promo_code, service=service))
        await ctx.send(embed=template_embeds.CONTINUE_ORDERING, ephemeral=True)


def setup(bot):
    bot.add_cog(EnterServicePromoCodeMenuReg(bot))
