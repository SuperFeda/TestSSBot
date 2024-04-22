# Цены всех услуг
SERVICE_PRICES: dict = {
    "skin64": 270,
    "rew_skin": 199,
    # "Скин 128x128": ,
    # "4D Скин": ,

    "model": 0,
    "anim_model": 0,
    "texture_model": 0,
    # "Модель + GeckoLib анимация + текстура": ,

    "cape": 99,
    "totem": 59,
    # "3D тотем со скином игрока": 0,
    "texture": 79,

    "letter_logo": 249,
    "letter_logo_2": 0,

    "characters_design": 700,

    # "Spigot плагин": 0
}

# Цены услуг с нестатическим ценником
NOT_STATIC_PRICE: dict = {
    "model": 149,
    "anim_model": 159,
    "texture_model": 159,
    "letter_logo_2": 249
}

# Сумма денег в рублях, которая будет отправляться в кошелек сотрудника после принятия заказа
SUMM_WORKER: dict = {
    "skin64": 90,
    "rew_skin": 70,

    "model": 0,
    "anim_model": 0,
    "texture_model": 0,

    "cape": 30,
    "totem": 25,
    "texture": 35,

    "letter_logo": 95,
    "letter_logo_2": 0,

    "characters_design": 350,
}

FROM_NAME_TO_CODE_SERVICE: dict = {
    "Скин 64x64": "skin64",
    "Скин 128x128": "skin128",
    "4D скин": "skin4d",
    "Перерисовка скина": "rew_skin",
    "Плащ": "cape",
    "4D Плащ": "cape4d",
    "Тотем": "totem",
    "3D Тотем": "totem3d",
    "Текстура блока/предмета": "texture",
    "Буквенный логотип": "letter_logo",
    "Логотип с кастомными буквами/доп. деталями": "letter_logo_2",
    "Анимированный буквенный логотип": "anim_letter_logo",
    "Генерация мира": "world_generation",
    "Обработка в Blender": "blender_render",
    "Дизайн персонажей": "characters_design",
    "Модель": "model",
    "Модель + текстура": "texture_model",
    "Модель + анимация": "anim_model",
    "Модель + анимация + текстура": "anim_texture_model",
    "Постройка": "structure",
    "Jigsaw структура": "jigsaw_structure",
    "Промокод на услугу": "service_promocode"
}
