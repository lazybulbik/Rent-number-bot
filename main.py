from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre, link
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InputFile, InputMedia
from aiogram.utils.helper import Helper, HelperMode, ListItem

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

import config
import db
import menu
import sms
import text

bot = Bot(config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

rent_list = {}


class Forms(Helper):
    mode = HelperMode.snake_case
    FIND_SERVICE = ListItem()


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    db.create_user(message)

    if message.text != '/start':
        referal_id = message.text.replace('/start ', '')

        if str(referal_id) != str(message.from_user.id):
            await bot.send_message(message.text.replace('/start ', ''), 'Вижу приглашенного вами друга!')
            db.update_data({'friends': db.get_data(referal_id)[0][2] + 1}, id=referal_id)

            if db.get_data(referal_id)[0][2] % 5 == 0:
                db.update_data({'activates': db.get_data(referal_id)[0][1] + 1}, referal_id)
                await bot.send_message(referal_id, 'Вы пригласили 5 друзей, как и обещали добавили Вам бесплатную активацию')

    await message.answer('Для работы с ботом подпишись на канал!', reply_markup=menu.check_menu)


@dp.message_handler(lambda message: not (message.entities), state=Forms.FIND_SERVICE[0])
async def find_services(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    check = sms.get_similar_service(message.text)

    if len(check) != 0:
        await message.answer('Вот что нашлось по вашему запросу:',
                             reply_markup=menu.get_find_srvices_menu(message.text))
        await state.reset_state()
    else:
        await message.answer('К сожалению, нам не удалось найти подходящий сервис. Попробуйте снова')


@dp.callback_query_handler(state='*')
async def call_back(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)

    if callback_query.data == menu.back_button.callback_data:
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text=text.main_menu,
                                    reply_markup=menu.main_menu)

        try:
            del rent_list[callback_query.from_user.id]
        except:
            pass

    elif callback_query.data == menu.back_to_services_button.callback_data:
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text='Выберите сервис',
                                    reply_markup=menu.get_services_menu())
        await state.reset_state()

    elif callback_query.data == menu.check_button.callback_data:
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text=text.main_menu,
                                    reply_markup=menu.main_menu)

    elif callback_query.data == menu.free_activation.callback_data:
        rent_list[callback_query.from_user.id] = {}
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text="Выберите страну",
                                    reply_markup=menu.get_contries_menu())

    elif 'country' in callback_query.data:
        rent_list[callback_query.from_user.id]['country'] = callback_query.data.split(':')[1]
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text='Выберите оператора',
                                    reply_markup=menu.get_operators_menu(
                                        rent_list[callback_query.from_user.id]['country']))

    elif 'operator' in callback_query.data:
        rent_list[callback_query.from_user.id]['operator'] = callback_query.data.split(':')[1]
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text="Выберите сервис",
                                    reply_markup=menu.get_services_menu())

    elif 'service' in callback_query.data:
        if callback_query.data == 'service:find_service':
            await state.set_state(Forms.FIND_SERVICE[0])
            await bot.edit_message_text(message_id=callback_query.message.message_id,
                                        chat_id=callback_query.from_user.id,
                                        text='Введите название сервиса, мы попробуем найти подходящий',
                                        reply_markup=menu.back_to_services_menu)
            return

        rent_list[callback_query.from_user.id]['service'] = callback_query.data.split(':')[1]
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text="Отлично! Все готово к аренде!",
                                    reply_markup=menu.buy_menu)

    elif callback_query.data == menu.buy_button.callback_data:
        print(rent_list[callback_query.from_user.id])

        activate = sms.rent_number(rent_list[callback_query.from_user.id])

        if activate['status'] == 'success':
            await bot.edit_message_text(message_id=callback_query.message.message_id,
                                        chat_id=callback_query.from_user.id,
                                        text=f'Вы успешно активировли номер телефона на 24 часа \n{activate["phone"]["number"]}',
                                        reply_markup=menu.get_check_sms_menu(activate['phone']['id']))

            del rent_list[callback_query.from_user.id]
        else:
            await bot.edit_message_text(message_id=callback_query.message.message_id,
                                        chat_id=callback_query.from_user.id,
                                        text=f'К сожалению мы не смогли найти свободные номера😞. Попробуйте выбрать другого оператора или страну',
                                        reply_markup=menu.get_contries_menu())

    elif 'check_sms' in callback_query.data:
        id = callback_query.data.split(':')[1]

        status = sms.get_sms(id)
        if 'STATUS_WAIT_CODE' in status:
            await bot.send_message(callback_query.from_user.id, 'Ожидание смс')

        elif 'STATUS_OK' in status:
            await bot.send_message(callback_query.from_user.id, status)

        elif 'STATUS_CANCEL' in status:
            await bot.send_message(callback_query.from_user.id, 'Аренда номера завершилась.')

        else:
            await bot.send_message(callback_query.from_user.id, 'Ожидание')

    elif callback_query.data == menu.rules.callback_data:
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text=text.rules,
                                    reply_markup=menu.back_menu)

    elif callback_query.data == menu.profile.callback_data:
        user = db.get_data(callback_query.from_user.id)[0]
        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text=f'Ваш профиль: \nid: {user[0]}\nКол-во бесплатных активаций: {user[1]} \nКол-во приглашенных друзей: {user[2]}',
                                    reply_markup=menu.back_menu)

    elif callback_query.data == menu.referal.callback_data:
        text_referal = 'Вы можете приглашать людей в нашего бота и получать за это дополнительные активации ' \
               f'\n Ваша ссылка для приглашения друга: https://t.me/FreeActivateBot?start={callback_query.from_user.id}'

        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    chat_id=callback_query.from_user.id,
                                    text=text_referal,
                                    reply_markup=menu.back_menu)

executor.start_polling(dp)
