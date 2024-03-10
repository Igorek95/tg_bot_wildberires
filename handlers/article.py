from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from db.orm import BaseAsyncORM
from handlers.start import MENU
from keyboards.inline_button import inline_keyboard
from keyboards.menu_choice import menu_choice_keyboard
from parsing_script import get_product_info

router = Router()


class Article(StatesGroup):
    choosing_article = State()


@router.message(F.text.in_(MENU[0]))
async def input_article(message: Message, state: FSMContext):
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, введи артикул товара",
    )
    await state.set_state(Article.choosing_article)



@router.message(Article.choosing_article)
async def get_info_goods(message: Message, state: FSMContext):
    article = message.text.lower()
    goods = await get_product_info(article)
    if goods == 'Ошибка артикула':
        await message.answer(
            text="Такого артикула не существует.\nПопробуй еще раз",
            reply_markup=inline_keyboard().as_markup(),
        )
        await state.set_state(Article.choosing_article)
    else:
        goods_string = ", \n".join([f"{hbold(key)} - {value}" for key, value in goods.items()])
        await message.answer(
            text=goods_string,
            reply_markup=inline_keyboard(article).as_markup(),
        )
        await state.clear()


@router.callback_query(F.data.startswith('subscribe'))
async def subscribe_button(callback: CallbackQuery):
    article = int(callback.data.split('_')[1])
    print(article)
    async with BaseAsyncORM() as sql:
        await sql.add_subscription(telegram_id=int(callback.from_user.id), article=article)
    await callback.message.answer(f'Вы nодписались на товар {article}')


@router.message(F.text == 'Остановить уведомления')
async def delete_subscriptions(message: Message):
    async with BaseAsyncORM() as sql:
        await sql.delete_subscriptions(telegram_id=int(message.from_user.id))
    await message.answer('Вы успешно отписались', reply_markup=menu_choice_keyboard(MENU))


@router.message(F.text == 'Получить информацию из БД')
async def receiving_data(message: Message):
    async with BaseAsyncORM() as sql:
        subscription_list = await sql.get_last_five_subs(telegram_id=int(message.from_user.id))
        message_list = []
        for sub in subscription_list:
            message_list.append(f'Артикул: {sub.article}\nСоздано: {sub.request_time}')
        message_str = '\n\n'.join(message_list)
        if not message_str:
            message_str = 'База Данных пустая'
        await message.answer(message_str, reply_markup=menu_choice_keyboard(MENU))
