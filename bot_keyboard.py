from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def charge(url: str, id: str) -> InlineKeyboardMarkup:
    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплата подписки", url=url)],
        [InlineKeyboardButton(text="Проверить оплату", callback_data=id)]
    ])
    return keyboard   


