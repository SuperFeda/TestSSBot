from disnake import Intents, Color
from disnake.ext.commands import Bot
from sqlite3 import connect, Cursor
from os import listdir, environ

from cogs.hadlers.utils import read_json

#####################################
#                                   #
# Самый говнокод из всех говнокодов #
#                                   #
# Python 3.11                       #
# disnake 2.9.1                     #
# colorama 0.4.6                    #
# numpy 1.26.4                      #
# pytz 2024.1                       #
#                                   #
#####################################


class SSBot(Bot):  # main класс бота
    BOT_CONFIG: dict = read_json("./data/bot_config.json")
    BOT_DATA: dict = read_json("./data/bot_data.json")
    SERVICES_NAME: dict = read_json("./data/services.json")
    PATH_TO_CLIENT_DB: str = "data/skylightbot_client_base.db"
    CLIENT_DB_CONNECTION: connect = connect(PATH_TO_CLIENT_DB)
    CLIENT_DB_CURSOR: Cursor = CLIENT_DB_CONNECTION.cursor()
    PATH_TO_WORKER_DB: str = "data/skylightbot_worker_base.db"
    WORKER_DB_CONNECTION: connect = connect(PATH_TO_WORKER_DB)
    WORKER_DB_CURSOR: Cursor = WORKER_DB_CONNECTION.cursor()
    PATH_TO_PROMO_CODES_DATA: str = "data/promo_codes.json"
    PATH_TO_CODES: str = "data/codes.json"
    PATH_TO_BOT_LOGS: str = "data/ssbot_logs.log"
    ORDER_ID_SYMBOLS: str = "1234567890AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"
    DEFAULT_COLOR: Color = Color.from_rgb(r=43, g=45, b=49)
    DONATION_ALERTS_COLOR: Color = Color.from_rgb(r=233, g=121, b=13)
    # NOT_STATIC_PRICE = [SERVICES_NAME[element]["name"] for element in SERVICES_NAME if SERVICES_NAME[element]["price_type"] == "nstatic"]
    NOT_STATIC_PRICE: tuple = (
        SERVICES_NAME["model"]["code"],
        SERVICES_NAME["anim_model"]["code"],
        SERVICES_NAME["texture_model"]["code"],
        SERVICES_NAME["anim_texture_model"]["code"],
        SERVICES_NAME["letter_logo_2"]["code"],
        SERVICES_NAME["structure"]["code"],
        SERVICES_NAME["jigsaw_structure"]["code"],
        SERVICES_NAME["world_generation"]["code"],
        SERVICES_NAME["service_promocode"]["code"],
        SERVICES_NAME["blender_render"]["code"]
    )

    def __init__(self):
        super().__init__(
            command_prefix="!",
            help_command=None,
            intents=Intents.all(),
            test_guilds=[1130086027885809675, 1214155025681489940],
            owner_id=875246294044643371
        )

    def load_cogs(self) -> None:
        """
        Загрузка когов бота.
        :return: None
        """
        # load bot commands
        for filename in listdir("./cogs/commands"):
            if filename.endswith(".py"):
                self.load_extension(f'cogs.commands.{filename[:-3]}')

        # load buttons
        for filename in listdir("./cogs/view/buttons"):
            if filename.endswith(".py"):
                self.load_extension(f'cogs.view.buttons.{filename[:-3]}')

        # load modals menus
        for filename in listdir("./cogs/view/modals_menu"):
            if filename.endswith(".py"):
                self.load_extension(f'cogs.view.modals_menu.{filename[:-3]}')

        # load select menus
        for filename in listdir("./cogs/view/select_menus"):
            if filename.endswith(".py"):
                self.load_extension(f'cogs.view.select_menus.{filename[:-3]}')

        # load rate system
        for filename in listdir("./cogs/systems/rate_system"):
            if filename.endswith(".py"):
                self.load_extension(f'cogs.systems.rate_system.{filename[:-3]}')

        self.load_extension("cogs.events")  # load bot events


SSBot.WORKER_DB_CURSOR.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        worker_salary,
        worker_tag,
        worker_display_name,
        worker_id
    )
""")

SSBot.CLIENT_DB_CURSOR.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        client_name,
        client_id,
        client_avatar,
        client_display_name,
        can_description,
        activated_promo_codes_list,
        active_promo_code,
        promo_code_activated,
        youtube_promo_code_counter,
        service_type,
        service_for_gift,
        service_description,
        stars,
        service_code,
        sending_time,
        order_message,
        order_embed,
        mail,
        vk_url,
        telegram_url
    )
""")


# CURRENCY = {
#     "RUB": "₽"
# }
#
# import json, asyncio, socketio
#
# sio = socketio.AsyncClient()
#
#
# @sio.on('connect')
# async def on_connect():
#     await sio.emit('add-user', {"token": environ["DA_SECRET"], "type": "alert_widget"})
#     print(f"{colorama.Fore.CYAN}sio emit{colorama.Fore.RESET}")
#
#
# @sio.on('donation')
# async def on_message(data):
#     print(f"{colorama.Fore.CYAN}donate was get{colorama.Fore.RESET} {data = }")
#     donation = json.loads(data)
#
#     DONATION_CHANNEL = BOT.get_channel(1214155027527110703)  # (SSBot.BOT_CONFIG["donation_channel_id"])
#     DA_LOGO = disnake.File("images/donation_alerts_logo.jpg", filename="donation_alerts_logo.jpg")
#
#     embed = disnake.Embed(title="Донат:", color=SSBot.DONATION_ALERTS_COLOR, description=donation['message'])
#     embed.set_author(name="DonationAlerts", icon_url="attachment://donation_alerts_logo.jpg")
#     try:
#         embed.add_field(name=f"Автор: {donation['username']}; Сумма оплаты: {donation['amount']}{CURRENCY[donation['currency']]}", value="", inline=False)
#     except:
#         embed.add_field(name=f"Автор: {donation['username']}; Сумма оплаты: {donation['amount']}{donation['currency']}", value="", inline=False)
#     embed.set_footer(text=f'id: {donation["id"]}; дата создания: {donation["date_created"]}')
#
#     await DONATION_CHANNEL.send(embed=embed, file=DA_LOGO)
#
#     # print(donation)
#
#     print(donation['username'])
#     print(donation['message'])
#     print(donation['amount'])
#     print(donation['currency'])
#
#
# async def sio_connection():
#     await sio.connect('wss://socket.donationalerts.ru:443', transports='websocket')
#     print(f"{colorama.Fore.CYAN}sio connected{colorama.Fore.RESET}")

########### Команда для тестов embed настороек
# @bot.slash_command()
# async def show_user(ctx, member: disnake.Member):
#     embed = disnake.Embed(title="Информация о пользователе", description=f"Никнейм: {member.display_name}", color=disnake.Color.blue())
#
#     if not member.avatar:
#         embed.set_author(name=member.display_name)
#     else:
#         embed.set_author(name=member.display_name, icon_url=member.avatar.url)
#
#     await ctx.send(embed=embed)
###########


# if __name__ == '__main__':
BOT = SSBot()

BOT.i18n.load("./lang/")  # Подгрузка файлов локализации
BOT.load_cogs()  # Подгрузка когов бота
# asyncio.run(sio_connection())

BOT.run(environ["SSBOT_TOKEN"])
