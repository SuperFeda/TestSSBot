import disnake

from disnake.ext import commands

from main import SSBot
from cogs.hadlers.embeds.ordering_embeds import WRITE_DESC_EMBED
from cogs.hadlers.embeds.template_embeds import ENTER_REWIEW_EMBED


class EnterDescriptionAgainButtonReg(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("EnterDescriptionAgainButton was added")
        self.bot.add_view(EnterDescriptionAgainButton(bot=self.bot))


class EnterDescriptionAgainButton(disnake.ui.View):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Ввести повторно", style=disnake.ButtonStyle.red, custom_id="enter_description_again_button")
    async def enter_desc_button(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message: disnake.Message = await ctx.channel.fetch_message(ctx.message.id)

        SSBot.CLIENT_DB_CURSOR.execute(
            "INSERT INTO settings (user_id, can_description) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET can_description=?",
            (ctx.author.id, True, True)
        )
        SSBot.CLIENT_DB_CONNECTION.commit()

        try:
            if "отзыв" in ctx.channel.name:
                await ctx.send(embed=ENTER_REWIEW_EMBED)
        except AttributeError:
            if isinstance(ctx.channel, disnake.PartialMessageable):
                await ctx.send(embed=WRITE_DESC_EMBED)

        await message.delete()

    def to_components(self):
        return super().to_components()


def setup(bot):
    bot.add_cog(EnterDescriptionAgainButtonReg(bot))
