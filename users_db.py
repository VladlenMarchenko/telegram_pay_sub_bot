import sqlite3
from datetime import datetime

# Функция для подключения к базе данных
def connect_db():
    return sqlite3.connect('users.db')

def create_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                username TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                subscription_date DATETIME NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                repeat_subscription INTEGER NOT NULL DEFAULT 0  -- Новая колонка для повторной подписки
            )
        ''')
        conn.commit()


# Функция для добавления пользователя
def add_user(username, chat_id):
    if check_username_exists(username):
        print(f"Пользователь {username} уже существует.")
        return  # Прекращаем выполнение функции, если пользователь уже есть

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_info (username, chat_id, subscription_date, is_active, repeat_subscription) VALUES (?, ?, ?, ?, ?)
        ''', (username, chat_id, date_time, 1, 0))  # Инициализируем повторную подписку на 0
        conn.commit()
        print(f"Пользователь {username} добавлен.")


def delete_user(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM user_info WHERE username = ?
        ''', (username,))
        conn.commit()
        print(f"Пользователь {username} удален.")

def get_all_users():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, chat_id, subscription_date, is_active, repeat_subscription FROM user_info')
        users = cursor.fetchall()
        return [
            {
                'username': user[0],
                'chat_id': user[1],
                'subscription_date': user[2],
                'is_active': user[3],
                'repeat_subscription': user[4]  # Убедитесь, что это поле включено
            }
            for user in users
        ]


def check_username_exists(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM user_info WHERE username = ?', (username,))
        return cursor.fetchone()[0] > 0 

# Функция для вывода всех пользователей
def display_users():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_info')
        users = cursor.fetchall()
        for user in users:
            print(f'Username: {user[0]}, Chat ID: {user[1]}, Subscription Date: {user[2]}, Active: {"Yes" if user[3] else "No"}')

def update_subscription_status(username, is_active):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_info SET is_active = ? WHERE username = ?
        ''', (is_active, username))
        conn.commit()
        print(f"Статус подписки для пользователя {username} обновлен на {'активен' if is_active else 'неактивен'}.")

async def get_user_status(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT is_active FROM user_info WHERE username = ?', (username,))
        result = cursor.fetchone()
        if result:
            return {'is_active': result[0]}
        return None

# Новая функция для получения пользователя по chat_id
def get_user_by_id(chat_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, chat_id, subscription_date, is_active FROM user_info WHERE chat_id = ?', (chat_id,))
        user = cursor.fetchone()
        if user:
            return {
                'username': user[0],
                'chat_id': user[1],
                'subscription_date': datetime.strptime(user[2], "%Y-%m-%d %H:%M:%S"),  # Преобразуем строку в datetime
                'is_active': bool(user[3])  # Преобразуем значение в булевый тип
            }
        return None  # Если пользователь не найден

# Функция для обновления статуса пользователя
def update_user_status(username, is_active):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_info SET is_active = ? WHERE username = ?
        ''', (is_active, username))
        conn.commit()
        print(f"Статус пользователя {username} обновлен на {'активен' if is_active else 'неактивен'}.")

# Новая функция для обновления даты подписки
def update_subscription_date(username, subscription_date):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_info SET subscription_date = ? WHERE username = ?
        ''', (subscription_date, username))
        conn.commit()
        print(f"Дата подписки для пользователя {username} обновлена на {subscription_date}.")

def increment_repeat_subscription(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_info SET repeat_subscription = repeat_subscription + 1 WHERE username = ?
        ''', (username,))
        conn.commit()
        print(f"Количество повторных подписок для пользователя {username} увеличено на 1.")


# Основной код
if __name__ == '__main__':
    display_users()  # Отображаем всех пользователей
    #create_table()