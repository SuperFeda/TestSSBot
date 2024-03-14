import disnake

from ssbot import SSBot


SS_LOGO = disnake.File("images/SkylightServices_new.png", filename="ss_logo.jpg")


START_ORDERING_EMBED = disnake.Embed(title="Здароу, я SkylightBot", color=disnake.Color.blurple()).set_image(url="attachment://ss_logo.jpg")
START_ORDERING_EMBED.add_field(name="С моей помощью вы сможете полностью оформить заказ: выбор услуги и создание описания - со всем этим буду помогать я.\nДля начала заполнения нажмите на кнопку \"Оформить заказ\".", value="")

WARNING_MESSAGE_EMBED = disnake.Embed(title="Уведомление", color=SSBot.DEFAULT_COLOR)
WARNING_MESSAGE_EMBED.add_field(
    name="Если я отправил не все изображения, что вы прикрепляли, то возможно это произошло из-за того, что ваши изображения имеют одинаковое название либо не разрешенный формат.",
    value="", inline=False
)
WARNING_MESSAGE_EMBED.add_field(
    name="Пожалуйста, перепроверьте эти факторы и повторно отправьте изображения.\nСписок поддерживаемый форматов файлов: `png`, `jpg`, `jpeg` и `gif`",
    value="", inline=False
)

CHECKING_ORDER_EMBED = disnake.Embed(title="Проверка содержимого заказа", color=disnake.Color.blurple())
CHECKING_ORDER_EMBED.add_field(name="Проверьте данные и запомните код заказа.\n**В тексте доната *ОБЯЗАТЕЛЬНО* напишите ваш Discord ник и код заказа, в ином случае заказ не будет выполнен.**", value="", inline=False)

WRITE_DESC_EMBED = disnake.Embed(title="Ввод описания", color=SSBot.DEFAULT_COLOR).add_field(
    name="Напишите в чат сообщение с описанием желаемого результата. Также вы можете прикрепить исходники в количестве до 10 штук в форматах: `png`, `jpg`, `jpeg` и `gif`.",
    value="", inline=False
)

WARN_PM_IS_OFF = disnake.Embed(title="Ошибка", color=disnake.Color.red()).add_field(
    name="Похоже, что у вас отключено принятие личных сообщений. Пожалуйста, следуйте инструкции ниже, для того, чтобы исправить это:",
    value="", inline=False
)

