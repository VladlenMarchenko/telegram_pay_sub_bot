import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.types import ChatJoinRequest
from aiogram.filters import Command
import Token
from payy import check_pay, create_paym
import bot_keyboard
import users_db
from datetime import datetime, timedelta
import json

# Инициализация бота 
bot = Bot(Token.Token)
dp = Dispatcher()

# Глобальные переменные для конфигурации
config = {}

# Функция для загрузки конфигурации из config.json
def load_config():
    global config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

# Функция для сохранения конфигурации в config.json
def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# Загрузка конфигурации при старте
load_config()

# Функция для периодической проверки конфигурации
async def update_config_periodically():
    while True:
        await asyncio.sleep(60)  # Проверяем каждые 60 секунд
        load_config()  # Загружаем конфигурацию

# Используйте переменные из загруженной конфигурации
def get_config_values():
    return (
        config.get('subscription_without_payment'),
        config.get('start_text'),
        config.get('channel_link_output'),
        config.get('payment_failed_'),
        config.get('subscription_paid'),
        config.get('renewal_subscription')
    )

# Функция для проверки статуса подписки пользователя
# Функция для проверки статуса подписки пользователя
async def is_user_active(username):
    user_status = await users_db.get_user_status(username)  # Получаем статус пользователя из БД
    return user_status is not None and user_status['is_active'] == 1  # Проверяем, активна ли подписка

# Функция для принятия юзеров после оплаты 
async def approve_request(chat_join: ChatJoinRequest):
    username = chat_join.from_user.username
    if await is_user_active(username):  # Проверяем статус подписки
        subscription_paid = config['subscription_paid']
        await bot.send_message(chat_id=chat_join.from_user.id, text=subscription_paid)
        await chat_join.approve()
    else:
        await bot.send_message(chat_id=chat_join.from_user.id, text="Ваша подписка неактивна. Пожалуйста, продлите подписку.")



# Функция начала работы с ботом 
@dp.message(Command("start"))
async def pay(message: types.Message):
    start_text = config['start_text']
    payment_link, payment = create_paym()
    await message.answer(start_text, reply_markup=bot_keyboard.charge(payment_link, payment))
    

@dp.chat_join_request(F.chat.id == Token.chenl_id)
async def handle_chat_join_request(chat_join: ChatJoinRequest):
    username = chat_join.from_user.username
    subscription_without_payment = config['subscription_without_payment']
    if is_user_active(username):
        await approve_request(chat_join)
    else:
        await bot.send_message(chat_id=chat_join.from_user.id, text=subscription_without_payment)

@dp.callback_query()
async def payment_verification(call: types.CallbackQuery):
    if call.message.text == config['start_text']:
        call_back = check_pay(call.data)
        if call_back:
            await bot.unban_chat_member(chat_id=Token.chenl_id, user_id=call.from_user.id)
            
            # Проверяем, существует ли пользователь в базе данных
            user = users_db.get_user_by_id(call.from_user.id)
            
            if user is None:
                # Пользователь не существует, добавляем его
                users_db.add_user(call.from_user.username, call.from_user.id)
                await bot.send_message(chat_id=call.from_user.id, text=config['channel_link_output'])
            else:
                # Пользователь существует, обновляем его статус на is_active и увеличиваем количество повторных подписок
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                users_db.update_user_status(call.from_user.username, is_active=True)
                users_db.update_subscription_date(call.from_user.username, current_time)
                users_db.increment_repeat_subscription(call.from_user.username)  # Увеличиваем количество повторных подписок
                await bot.send_message(chat_id=call.from_user.id, text=config['channel_link_output'])
                
            print(users_db.display_users())
        else:
            await bot.send_message(chat_id=call.from_user.id, text=config['payment_failed_'])


            
import asyncio
from datetime import datetime, timedelta
import Token  # Убедитесь, что у вас есть этот модуль
import users_db  # Импортируйте вашу базу данных пользователей

async def check_subscriptions():
    while True:
        await asyncio.sleep(3600)  # Проверяем раз в час
        now = datetime.now()
        users = users_db.get_all_users()  
        
        for user in users:
            subscription_date_str = user['subscription_date']  # Получаем строку даты
            is_active = user['is_active']  # Получаем статус подписки

            # Преобразуем строку в datetime
            try:
                subscription_date = datetime.strptime(subscription_date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"Ошибка преобразования даты для пользователя {user['username']}: {subscription_date_str}")
                continue  # Пропускаем пользователя, если дата некорректна

            # Проверяем, истекла ли подписка
            if now - subscription_date > timedelta(days=30) and is_active:
                await bot.ban_chat_member(chat_id=Token.chenl_id, user_id=user['chat_id'])
                await bot.send_message(chat_id=user['chat_id'], text=config['renewal_subscription'])
                
                # Обновляем статус подписки
                users_db.update_subscription_status(user['username'], is_active=0)  # Устанавливаем is_active в 0


async def main():
    asyncio.create_task(check_subscriptions())
    asyncio.create_task(update_config_periodically())  # Запускаем задачу обновления конфигурации
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
