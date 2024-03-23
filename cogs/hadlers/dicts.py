from main import SSBot

# Цены всех услуг
SERVICE_PRICES = {
    SSBot.SKIN64: 270,
    # "Скин 128x128": ,
    # "4D Скин": ,

    SSBot.MODEL: 0,
    SSBot.ANIM_MODEL: 0,
    SSBot.TEXTURE_MODEL: 0,
    # "Модель + GeckoLib анимация + текстура": ,

    SSBot.CAPE: 99,
    SSBot.TOTEM: 59,
    # "3D тотем со скином игрока": 0,
    SSBot.TEXTURE: 79,

    SSBot.LETTER_LOGO: 249,
    SSBot.LETTER_LOGO_2: 0,

    SSBot.CHARACTERS_DESIGN: 700,

    # "Spigot плагин": 0
}

# Цены услуг с нестатическим ценником
NOT_STATIC_PRICE = {
    SSBot.MODEL: 149,
    SSBot.ANIM_MODEL: 159,
    SSBot.TEXTURE_MODEL: 159,
    SSBot.LETTER_LOGO_2: 249
}

# Сумма денег в рублях, которая будет отправляться в кошелек сотрудника после принятия заказа
SUMM_WORKER = {
    SSBot.SKIN64: 90,

    SSBot.MODEL: 0,
    SSBot.ANIM_MODEL: 0,
    SSBot.TEXTURE_MODEL: 0,

    SSBot.CAPE: 30,
    SSBot.TOTEM: 25,
    SSBot.TEXTURE: 35,

    SSBot.LETTER_LOGO: 95,
    SSBot.LETTER_LOGO_2: 0,

    SSBot.CHARACTERS_DESIGN: 350,
}

# Вид того, как должен выглядеть файл promo_codes.json из папки data без данных о промокодах (idk зачем это здесь)
BASE_PC_FILE = {
    "common_code": {},
    "youtube_code": {},
    "service_code": {}
}
