import disnake

from main import SSBot

LOGOS = disnake.File("images/logos.png", filename="logos.jpg")

SKIN_QUESTION_EMBED = disnake.Embed(
    title="Дополнительные вопросы",
    color=SSBot.DEFAULT_COLOR,
    description="Для того чтобы мы выполнили ваш заказа так, как хотите вы, нам нужно знать ещё кое-какую информацию. Пожалуйста, ответьте на вопросы ниже:"
).add_field(name="1) Ваш скин должен иметь стандартные руки или тонкие?", value="", inline=False)

TOTEM_QUESTION_EMBED = disnake.Embed(
    title="Дополнительные вопросы",
    color=SSBot.DEFAULT_COLOR,
    description="Для того чтобы мы выполнили ваш заказа так, как хотите вы, нам нужно знать ещё кое-какую информацию. Пожалуйста, ответьте на вопросы ниже:"
).add_field(
    name="1) Как нам реализовать добавление тотема в игру?",
    value="Мы предоставляем два способа добавления тотема в Minecraft:\n`(1)` Замена текстуры тотема бессмертия по умолчанию.\n`(2)` Замена текстуры тотема по переименованию в наковальне. [Нужен OptiFine]\nЛибо мы можем просто отправить вам готовую текстуру и вы сами с ней разберётесь.",
    inline=False
)

LOGO_QUESTION_EMBED = disnake.Embed(
    title="Дополнительные вопросы",
    color=SSBot.DEFAULT_COLOR,
    description="Для того чтобы мы выполнили ваш заказа так, как хотите вы, нам нужно знать ещё кое-какую информацию. Пожалуйста, ответьте на вопросы ниже:"
).add_field(name="1) В логотипе должны быть пробелы между словами?", value="", inline=False).set_image(url="attachment://logos.jpg")

CHARACTERS_QUESTION_EMBED = disnake.Embed(
    title="Дополнительные вопросы",
    color=SSBot.DEFAULT_COLOR,
    description="Для того чтобы мы выполнили ваш заказа так, как хотите вы, нам нужно знать ещё кое-какую информацию. Пожалуйста, ответьте на вопросы ниже:"
).add_field(name="1) На персонаже должны быть тени?", value="", inline=False).add_field(name="2) У персонажа должен быть контур?", value="", inline=False)

