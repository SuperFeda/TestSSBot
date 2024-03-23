import disnake

from main import SSBot
from cogs.hadlers.utils import create_embed


WARN_MANY_IMAGES_EMBED = create_embed(title="Слишком много изображений", color=disnake.Color.red(), content="Отправить можно максимум **10** изображений.")
WARN_MANY_IMAGES_FOR_REVIEW_EMBED = create_embed(title="Слишком много изображений", color=disnake.Color.red(), content="Отправить можно максимум **одно** изображение.")
WARN_LONG_DESC_EMBED = create_embed(title="Слишком длинное описание", color=disnake.Color.red(),  content="Описание должно вмещать в себя до **1020** символов.")
WARN_SHORT_DESC_EMBED = create_embed(title="Слишком короткое описание", color=disnake.Color.red(), content="Описание должно быть длинне **10** символов.")
FEEDBACK_EMBED = create_embed(title="Отзывы", color=SSBot.DEFAULT_COLOR, content=f'**Отзывы** можно посмотреть здесь: <#{SSBot.BOT_DATA["feedback_channel_id"]}>')
PS_EMBED = create_embed(title="Пользовательское соглашение", color=SSBot.DEFAULT_COLOR, content=f'**Пользовательское соглашение** можно прочитать здесь: <#{SSBot.BOT_DATA["user_agreement_channel_id"]}>')
ADDITIONAL_WORK_EXAMPLES = create_embed(title="Дополнительные примеры работ", color=SSBot.DEFAULT_COLOR, content=f'**Дополнительные примеры работ** можно посмотреть здесь: <#{SSBot.BOT_DATA["additional_examples_channel_id"]}>')
WARN_ACTIVATED_PROMO_CODE_AVAILABLE_EMBED = create_embed(title="Промокод не активирован", color=disnake.Color.red(), content="У вас уже есть активированный промокод.")
WARN_PROMO_CODE_WAS_PREVIOUSLY_ENTERED_EMBED = create_embed(title="Промокод недействителен", color=disnake.Color.red(), content="Данный промокод уже был введён ранее на вашем аккаунте.")
WARN_USER_NOT_IN_LIST = create_embed(title="Промокод недействителен", color=disnake.Color.red(), content="Вы не можете активировать этот промокод потому что вас не в списке пользователей, которым он доступен.")
WARN_PROMO_CODE_CANNOT_BE_USED = create_embed(title="Промокод недействителен", color=disnake.Color.red(), content="Этот промокод больше нельзя использовать.")
WARN_PROMO_CODE_NOT_IN_DB = create_embed(title="Промокод недействителен", color=disnake.Color.red(), content="Такого промокода нету в базе данных.")
CONTINUE_ORDERING = create_embed(title="Продолжение оформление заказа", color=SSBot.DEFAULT_COLOR, content=f"Для того чтобы продолжить оформление заказа перейдите в личный диалог со мной.")
REQUEST_WAS_SEND = create_embed(title="Запрос отправлен", color=SSBot.DEFAULT_COLOR, content="Ваш запрос был отправлен, скоро с вами свяжутся.")
REPORT_WAS_SEND = create_embed(title="Репорт отправлен", color=SSBot.DEFAULT_COLOR, content="Ваша жалоба была отправлена менеджерам.")
DOESNT_HAVE_PERMISSION = create_embed(title="Не достаточно прав", color=disnake.Color.red(),  content="У вас нет прав на использование этой команды.")
SALARIES_CANCELLED_EMBED = create_embed(title="База данных обновлена", color=SSBot.DEFAULT_COLOR, content="Зарплаты аннулированы.")
ENTER_DESC_EMBED = create_embed(title="Ввод описания", color=SSBot.DEFAULT_COLOR, content="Напишите в чат сообщение с описанием желаемого результата. Также вы можете прикрепить исходники в количестве до 10 штук в форматах: `png`, `jpg`, `jpeg` и `gif`.")
NOTIFICATION_SEND_EMBED = create_embed(title="Уведомление отправлено", color=SSBot.DEFAULT_COLOR, content="Я уведомил менеджеров о том, что у вас появился срочный вопрос. Скоро вам ответят.")
ENTER_REWIEW_EMBED = create_embed(title="Ввод описания", color=SSBot.DEFAULT_COLOR, content="Напишите в чат ваш отзыв о сервисе. Также вы можете прикрепить **одну** фотографию в формате: `png`, `jpg`, `jpeg` и `gif`.")
BANNED_FILE_EMBED = create_embed(title="Файл заблокирован", color=disnake.Color.red(), content="**Файл был заблокирован из-за того, что его формат не поддерживается.**")
REVIEW_CHECKING_EMBED = create_embed(title="Проверка", color=SSBot.DEFAULT_COLOR, content="Проверьте, всё ли написано верно. Если нет, то вернитесь в самое начало создания отзыва.")
START_CREATING_REVIEW_EMBED = create_embed(title="Создание отзыва", color=SSBot.DEFAULT_COLOR, content='Для начала выберите кол-во звезд:')



