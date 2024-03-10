from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def inline_keyboard(article):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Подписаться", callback_data=f"subscribe_{article}")
    )
    return builder
