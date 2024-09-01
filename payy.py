import yookassa
import Token
import json

import json

# Глобальные переменные для конфигурации
config = {}

# Функция для загрузки конфигурации из config.json
def load_config():
    global config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Файл config.json не найден. Будет использована пустая конфигурация.")
        config = {}  # Инициализация пустой конфигурации
    except json.JSONDecodeError:
        print("Ошибка при чтении файла config.json. Проверьте формат JSON.")
        config = {}  # Инициализация пустой конфигурации

# Функция для сохранения конфигурации в config.json
def save_config():
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении файла config.json: {e}")

# Загрузка конфигурации при старте приложения
load_config()

# Используйте переменные из загруженной конфигурации
def get_config_values():
    return (
        config.get('payment', {}).get('value'),
        config.get('payment', {}).get('description'),
    )

def create_paym():
    yookassa.Configuration.account_id = Token.Api_id
    yookassa.Configuration.secret_key = Token.Api_key

    #value, description = get_config_values()

    # Проверка значения перед преобразованием
    #if value is None:
     #   raise ValueError("Сумма платежа не задана в конфигурации.")
    
    #try:
     #   value = int(value)  # Преобразуем значение в целое число
    #except ValueError:
     #   raise ValueError("Сумма платежа должна быть числом.")

    payment = yookassa.Payment.create({
        "amount": {
            "value": config["value"],
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/testerssssssss_bot"
        },
        "description": config["description"],
        "capture": True
    })

    url = payment.confirmation.confirmation_url
    return url, payment.id

def check_pay(id):
    payment = yookassa.Payment.find_one(id)
    return payment.status == "succeeded"

if __name__ == "__main__":
    try:
        print(create_paym())
    except Exception as e:
        print(f"Ошибка при создании платежа: {e}")
