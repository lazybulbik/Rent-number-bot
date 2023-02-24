from smsactivate.api import SMSActivateAPI
from fuzzywuzzy import fuzz
import tables

import config

sa = SMSActivateAPI(config.SMS_TOKEN)
sa.debug_mode = False  # Optional action. Required for debugging


def get_countries():
    free_contries = list(sa.getRentServicesAndCountries(time=24)['countries'].values())
    countries = {}
    contries_raw = sa.getCountries()

    result = {}

    for i in contries_raw:
        country = contries_raw[i]
        countries[country['id']] = country['rus']

    count = 0
    for key in free_contries:
        if count == 15:
            break
        result[key] = countries[key]
        count += 1

    return result


def get_operators(country):
    free_operators = list(sa.getRentServicesAndCountries(time=24, country=country)['operators'].values())
    result = {}
    for i in free_operators:
        result[i] = i

    return result


def get_services():
    result = {'fb': 'Facebook', 'wa': 'Whatsapp', 'dr': 'OpenAI', 'ig': 'Instagram', 'tg': 'Telegram',
              'go': 'Google,youtube,Gmail', 'vi': 'Viber', 'mm': 'Microsoft', 'ds': 'Discord',
              'hw': 'Alipay/Alibaba/1688', 'me': 'Line messenger', 'am': 'Amazon'}

    return result


def get_similar_service(query):
    services = list(tables.services.values())
    result = {}

    for service in services:
        # print(service, fuzz.ratio(query, service))
        if fuzz.ratio(query.lower(), service.lower()) > 70:
            result[get_key(tables.services, service)] = service

    return result


def rent_number(params):
    activate = sa.getRentNumber(service=params['service'],
                                time=24,
                                operator=params['operator'],
                                country=params['country'])
    return activate


def get_sms(id):
    activation = sa.getStatus(id=id)
    return activation


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k

