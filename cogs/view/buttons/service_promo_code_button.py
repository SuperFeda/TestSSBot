import disnake

from disnake.ext import commands

from cogs.view.modals_menu.enter_service_promo_code import EnterServicePromoCodeMenu


class ServicePromoCodeButtonReg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ServicePromoCodeButton was added")
        self.bot.add_view(ServicePromoCodeButton(bot=self.bot))


class ServicePromoCodeButton(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Ввести промокод", style=disnake.ButtonStyle.blurple, custom_id="service_promo_code_button")
    async def promo_code_button(self, button: disnake.ui.Button, ctx: disnake.AppCmdInter):
        await ctx.response.send_modal(modal=EnterServicePromoCodeMenu(self.bot))

    def to_components(self):
        return super().to_components()


def setup(bot):
    bot.add_cog(ServicePromoCodeButtonReg(bot))
