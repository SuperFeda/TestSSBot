import json

from disnake import Member, Embed, Color, File
from os import remove, listdir, rmdir
from numpy import arange
from random import choice
from colorama import Fore


async def var_test(variable: vars) -> None:
    """
    def для тестирования переменных
    :param variable: переменная
    :return: None
    """
    print(f"{Fore.CYAN}var type: {type(variable)}\n{variable = }{Fore.RESET}")


def read_json(path: str) -> dict:
    """
    Чтение JSON файла
    :param path: путь к JSON файлу
    :return: содержимое JSON
    """
    with open(path, 'r') as json_file:
        return json.load(json_file)


async def async_read_json(path: str) -> dict:
    """
    Чтение JSON файла (async)
    :param path: путь к JSON файлу
    :return: содержимое JSON
    """
    with open(path, 'r') as json_file:
        return json.load(json_file)


async def write_json(path: str, data: dict) -> None:
    """
    Запись новых данных в JSON файл
    :param path: путь к JSON файлу
    :param data: данные, которые должны быть записаны
    :return: None
    """
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


async def string_to_list(string: str) -> list:
    """
    Конвертирование строки "123456789,FFFFFFFFF,AAAAAAAAA," в список ['23456789', 'FFFFFFFFF', 'AAAAAAAAA'].
    Используется для проверки: находится ли промокод в списке введенных пользователем.
    :param string: Строка для конвертирования
    :return: Список, получаемый после конвертирования `string`
    """
    list_ = []
    result = ""
    for symbol in string:
        if symbol == ",":
            list_.append(result.replace(result[0], ""))
            result = ""
        result += symbol

    return list_


async def calc_percentage(promo_code: str, price: int) -> int | None:
    """
    Подсчет стоимости заказа с учетом % скидки промокода
    :param promo_code: название промокода
    :param price: цена услуги
    :return: стоимость оплаты за заказ с учетом промокода.
    """
    from main import SSBot

    promo_codes_json = await async_read_json(path=SSBot.PATH_TO_PROMO_CODES_DATA)
    len_promo_code = len(promo_code)

    if len_promo_code == 10:
        return price - (price * promo_codes_json["common_code"][promo_code]["discount_rate"] / 100)
    elif len_promo_code == 17:
        return price - (price * promo_codes_json["youtube_code"][promo_code]["discount_rate"] / 100)
    else:
        return print(f"{Fore.RED}[ERR]{Fore.RESET} Error in calc_percentage def")


async def get_promocode_type(promocode_name: str) -> str:
    """
    Определение типа промокода по его имени
    :param promocode_name: имя промокода
    :return: тип промокода
    """
    len_pmn = len(promocode_name)
    type_ = None

    if len_pmn == 10:
        type_ = "common_code"
    elif len_pmn == 15:
        type_ = "service_code"
    elif len_pmn == 17:
        type_ = "youtube_code"

    return type_


async def generate_random_combination(length: int) -> str:
    """
    Генерация ID заказа
    :param length: длинна ID
    :return: ID заказа
    """
    from main import SSBot

    return ''.join(choice(SSBot.ORDER_ID_SYMBOLS) for _ in arange(length))


async def color_order(service: str) -> Color:
    """
    Получение цвета для левой полоски Embed
    :param service: заказываемая услуга
    :return: цвет для embed
    """
    from main import SSBot

    if service in (SSBot.SKIN64, SSBot.SKIN128, SSBot.SKIN_4D):
        return Color.blue()
    elif service in (SSBot.MODEL, SSBot.ANIM_MODEL, SSBot.ANIM_TEXTURE_MODEL, SSBot.TEXTURE_MODEL):
        return Color.brand_red()
    elif service in (SSBot.CAPE, SSBot.TOTEM, SSBot.TOTEM_3D, SSBot.TEXTURE):
        return Color.orange()
    elif service in (SSBot.LETTER_LOGO, SSBot.LETTER_LOGO_2):
        return Color.blurple()
    elif service in (SSBot.CHARACTERS_DESIGN):
        return Color.dark_orange()
    elif service in (SSBot.WORLD_GENERATION, SSBot.JIGSAW_STRUCTURE):
        return Color.magenta()
    else:
        return Color.default()


async def color_archive_request(type: str) -> Color:
    """
    Получение цвета для левой полоски Embed
    :param type: тип запроса
    :return: цвет для embed
    """
    if type == "покупка":
        return Color.blue()
    elif type == "предложение":
        return Color.green()
    else:
        return Color.default()


async def get_files_disnake(path: str) -> list:
    """
    Получение файлов из папки
    :param path: путь к папке
    :return: список файлов из папки
    """
    picture_for_send = []
    for image_for_send in listdir(path):
        picture_for_send.append(File(path+f"{image_for_send}"))

    return picture_for_send


async def get_files(path: str) -> list:
    """
    Получение файлов из папки
    :param path: путь к папке
    :return: список файлов из папки
    """
    picture_for_send = []
    for image_for_send in listdir(path):
        picture_for_send.append(path+f"{image_for_send}")

    return picture_for_send


async def get_avatar(ctx_user_avatar: Member.avatar) -> Member.avatar or None:
    """
    Получение аватара пользователя
    :param ctx_user_avatar: аватар юзера
    :return: получение аватара либо None, если аватара нет
    """
    if not ctx_user_avatar:
        avatar = None
    else:
        avatar = ctx_user_avatar.url

    return avatar


async def star_count_conv(count: int) -> str:
    """
    Конвертирование числа в эмодзи звёзды
    :param count: кол-во звёзд, которое должно получится в итоге
    :return: строка содержащая звезды
    """
    return "🌟"*count


def create_embed(title: str, color: Color, content: str) -> Embed:
    """
    Создание Embed по определенному шаблону
    :param title: Заголовок Embed
    :param color: Цвет полоски Embed
    :param content: Содержимое Embed (256 символов макс.)
    :return: Embed
    """
    embed = Embed(title=title, color=color)
    embed.add_field(name=content, value="")

    return embed


async def delete_files_from_cache(author_name) -> None:
    """
    Удаление файлов из кеш-папки юзера
    :param author_name: name автора
    :return: None
    """
    for file in listdir(f"cache/{author_name}/"):
        remove(f"cache/{author_name}/{file}")
    rmdir(f"cache/{author_name}")


async def convert_value_to_service_name(value: str) -> str:
    """
    Конвертирование ключа в название услуги.
    Пример: skin64 ==> Скин 64х64.
    :param value: Ключ по которому будет производиться конвертация.
    :return: Конвертированное название.
    """
    from main import SSBot

    match value:
        case "skin64":
            return SSBot.SKIN64
        case "skin128":
            return SSBot.SKIN128
        case "skin4d":
            return SSBot.SKIN_4D
        case "cape":
            return SSBot.CAPE
        case "totem":
            return SSBot.TOTEM
        case "texture":
            return SSBot.TEXTURE
        case "letter_logo":
            return SSBot.LETTER_LOGO
        case "letter_logo_2":
            return SSBot.LETTER_LOGO_2
        case "anim_letter_logo":
            return SSBot.ANIM_LETTER_LOGO
        case "world_generation":
            return SSBot.WORLD_GENERATION
        case "blender_render":
            return SSBot.BLENDER_RENDER
        case "characters_design":
            return SSBot.CHARACTERS_DESIGN
        case "model":
            return SSBot.MODEL
        case "texture_model":
            return SSBot.TEXTURE_MODEL
        case "anim_model":
            return SSBot.ANIM_MODEL
        case "anim_texture_model":
            return SSBot.ANIM_TEXTURE_MODEL
        case "structure":
            return SSBot.STRUCTURE
        case "jigsaw_structure":
            return SSBot.JIGSAW_STRUCTURE


