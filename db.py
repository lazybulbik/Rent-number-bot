import sqlite3


def create_user(data):
    insert_data = [(data.from_user.id, 1, 0)]
    users_id = [user[0] for user in get_data()]

    with sqlite3.connect('db/database.db') as db:
        cursor = db.cursor()

        if str(data.from_user.id) in users_id:
            return

        query = ''' INSERT INTO users(id, activates, friends) VALUES(?, ?, ?)'''

        cursor.executemany(query, insert_data)
        db.commit


def get_data(user_id=None):
    '''
    получает данные из бд

    user_id - поиск осуществится по айди юзера, если None возращаеются все данные
    usenname - поиск осуществится по имени пользователя, если None возращаеются все данные
    '''

    with sqlite3.connect('db/database.db') as db:
        cursor = db.cursor()

        if user_id != None:
            select_query = '''SELECT * from users where id = ?'''
            cursor.execute(select_query, (user_id,))

        elif user_id == None:
            select_query = '''SELECT * from users'''
            cursor.execute(select_query)

        data = cursor.fetchall()

        return data


def update_data(data: dict(), id=None):
    '''
    обновление данных в бд

    data - словарь в формате <колонна>:<значение> (можно несколько)
    id - обновление произойдет только у определенного пользователя, если None - у всех
    '''

    with sqlite3.connect('db/database.db') as db:
        cursor = db.cursor()

        if id != None:
            for key in data:
                update_data = (data[key], id)

                query = f'UPDATE users SET {key} = ? where id = ?'
                cursor.execute(query, update_data)

        else:
            for key in data:
                update_data = (data[key],)

                query = f'UPDATE users SET {key} = ?'
                cursor.execute(query, update_data)

        db.commit()

