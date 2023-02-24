from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.helper import Helper, HelperMode, ListItem

import sms

check_button = InlineKeyboardButton('Проверить', callback_data='check_subcribe')
check_menu = InlineKeyboardMarkup().add(check_button)

back_button = InlineKeyboardButton('Главное меню', callback_data='back')
back_menu = InlineKeyboardMarkup().add(back_button)

back_to_services_button = InlineKeyboardButton('Назад', callback_data='back_to_services')
back_to_services_menu = InlineKeyboardMarkup().add(back_to_services_button)

buy_button = InlineKeyboardButton('Арендовать номер', callback_data='buy')
buy_menu = InlineKeyboardMarkup().add(buy_button).add(back_button)

free_activation = InlineKeyboardButton('Бесплатная активация', callback_data='free_activation')
rules = InlineKeyboardButton('Правила', callback_data='rules')
profile = InlineKeyboardButton('Профиль', callback_data='profile')
referal = InlineKeyboardButton('Получить дополнительные активации', callback_data='referal')
main_menu = InlineKeyboardMarkup()
main_menu.add(free_activation)
main_menu.add(rules, profile)
main_menu.add(referal)


def get_contries_menu():
    countries = sms.get_countries()

    buttons = [InlineKeyboardButton(countries[b], callback_data=f'country:{str(b)}') for b in countries]
    menu = InlineKeyboardMarkup(row_width=3).add(*buttons)
    menu.add(back_button)
    return menu


def get_operators_menu(country):
    operators = sms.get_operators(country)

    buttons = [InlineKeyboardButton(operators[b], callback_data=f'operator:{str(b)}') for b in operators]
    menu = InlineKeyboardMarkup(row_width=3).add(*buttons)
    menu.add(back_button)
    return menu


def get_services_menu():
    services = sms.get_services()

    buttons = [InlineKeyboardButton(services[b], callback_data=f'service:{str(b)}') for b in services]
    find_button = InlineKeyboardButton('Найти сервис', callback_data='service:find_service')

    menu = InlineKeyboardMarkup(row_width=3)
    menu.add(find_button)
    menu.add(*buttons)
    menu.add(back_button)
    return menu


def get_find_srvices_menu(query):
    services = sms.get_similar_service(query)
    buttons = [InlineKeyboardButton(services[b], callback_data=f'service:{str(b)}') for b in services]
    menu = InlineKeyboardMarkup(row_width=3)
    menu.add(*buttons)
    return menu


def get_check_sms_menu(id):
    check_sms_button = InlineKeyboardButton('Проверить входящие смс', callback_data=f'check_sms:{id}')
    check_sms_menu = InlineKeyboardMarkup().add(check_sms_button).add(back_button)
    return check_sms_menu