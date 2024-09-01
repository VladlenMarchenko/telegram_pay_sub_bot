from flask import Flask, request, render_template_string, jsonify, redirect, url_for, session, render_template
import Token
import users_db  # Импортируйте ваш модуль с функциями работы с пользователями
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Задайте секретный ключ для сессий



# Загрузка конфигурации из config.json
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Сохранение конфигурации в config.json
def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверка логина и пароля
        if username == Token.adm_log and password == Token.adm_password:
            session['logged_in'] = True  # Устанавливаем флаг сессии
            return redirect(url_for('index'))  # Перенаправляем на админ-панель
        else:
            return "Неверный логин или пароль."

    return render_template_string('''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/5.1.0/css/bootstrap.min.css" rel="stylesheet">
    <title>Login</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #E0C4FC; /* Установка цвета фона */
            font-family: 'Roboto', sans-serif; /* Применение шрифта Roboto */
        }
        .login-container {
            width: 400px; /* Увеличение ширины контейнера */
            padding: 30px; /* Увеличение отступов внутри контейнера */
            border: 1px solid #ced4da;
            border-radius: 5px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .form-control {
            height: 50px; /* Увеличение высоты полей ввода */
            font-size: 16px; /* Увеличение размера шрифта */
        }
        .btn {
            color: #313133;
            background: linear-gradient(90deg, rgba(129,230,217,1) 0%, rgba(79,209,197,1) 100%);
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 10px 20px; /* Увеличение отступов кнопки */
            margin: 20px 0 0; /* Отступ сверху для кнопки */
            border: none;
            border-radius: 50px;
            position: relative;
            z-index: 1;
            transition: all 0.3s ease-in-out 0s;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2 class="text-center">Login</h2>
        <form method="POST" class="mt-3">
            <div class="mb-3">
                <input type="text" class="form-control" name="username" placeholder="Логин" required>
            </div>
            <div class="mb-3">
                <input type="password" class="form-control" name="password" placeholder="Пароль" required>
            </div>
            <button type="submit" class="btn w-100">Войти</button>
        </form>
    </div>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/5.1.0/js/bootstrap.bundle.min.js"></script>
</body>
</html>

    ''')



@app.route('/admin', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Если не авторизован, перенаправляем на страницу логина

    config = load_config()  # Загружаем конфигурацию

    return render_template_string('''
<!doctype html>
<html lang="ru">
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/5.1.0/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <title>Admin Panel</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif; /* Применение шрифта Roboto */
            background-color: #E6E6FA; /* Установка цвета фона */
            color: #000000; /* Цвет текста */
        }
        .form-control {
            margin-bottom: 15px; /* Установка отступа между полями ввода */
            width: 100%; /* Установка ширины полей ввода на 100% */
        }
        .btn {
            color: #313133;
            background: linear-gradient(90deg, rgba(129,230,217,1) 0%, rgba(79,209,197,1) 100%);
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 8px 20px;
            margin: 0 15px;
            border: none;
            border-radius: 50px;
            position: relative;
            z-index: 1;
            transition: all 0.3s ease-in-out 0s;
        }
        .btn-update {
            margin-bottom: 20px; /* Увеличение отступа снизу */
        }
        .btn-list {
            margin-bottom: 20px; /* Увеличение отступа снизу */
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h2>Admin Panel</h2>
        <form id="configForm" class="mt-3">
            <div class="mb-3">
                <label for="admin_id" class="form-label">Айди админа</label>
                <input type="text" class="form-control" id="admin_id">
            </div>
            {% for key, value in config.items() %}
                <div class="mb-3">
                    <label for="{{ key }}" class="form-label">
                        {% if key == 'value' %}Стоимость подписки
                        {% elif key == 'description' %}Название товара
                        {% elif key == 'subscription_without_payment' %}Подписка без оплаты
                        {% elif key == 'start_text' %}Начальный текст
                        {% elif key == 'channel_link_output' %}Ссылка на канал
                        {% elif key == 'payment_failed_' %}Оплата не прошла
                        {% elif key == 'subscription_paid' %}Подписка оплачена
                        {% elif key == 'renewal_subscription' %}Продление подписки
                        {% else %}{{ key }}  <!-- Если ключ не найден, отображаем его как есть -->
                        {% endif %}
                    </label>
                    <input type="text" class="form-control" name="{{ key }}" value="{{ value }}">
                </div>
            {% endfor %}
            <button type="button" class="btn btn-update" onclick="updateConfig()">Обновить переменные</button>
            <button type="button" class="btn btn-list" onclick="listUsers()">Показать всех пользователей</button>
        </form>
        <div id="response" class="mt-3"></div>
        <div id="userList" class="mt-3"></div>
    </div>
    <!-- Bootstrap JavaScript -->
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/5.1.0/js/bootstrap.bundle.min.js"></script>
    <script>
        function updateConfig() {
            const formData = new FormData(document.getElementById('configForm'));
            const adminId = document.getElementById('admin_id').value;
            formData.append('admin_id', adminId);
            fetch('/update_config', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').innerText = data.message;
            })
            .catch(error => {
                document.getElementById('response').innerText = 'Ошибка: ' + error;
            });
        }

        function listUsers() {
            fetch('/list_users')
            .then(response => response.text())
            .then(data => {
                document.getElementById('userList').innerHTML = data;
            })
            .catch(error => {
                document.getElementById('userList').innerText = 'Ошибка: ' + error;
            });
        }
    </script>
</body>
</html>
    ''', config=config)  # Передаем оригинальный config в шаблон



@app.route('/update_config', methods=['POST'])
def update_config():
    admin_id = request.form.get('admin_id')
    
    # Проверка на пустое значение admin_id
    if not admin_id:
        return jsonify({"message": "Пожалуйста, введите Admin ID."})

    try:
        if int(admin_id) == Token.admin_id:
            config = load_config()  # Загружаем конфигурацию
            # Обновление переменных
            for key in config.keys():
                if key in request.form:
                    config[key] = request.form[key]
            
            # Сохранение изменений в файл
            save_config(config)
            return jsonify({"message": "Переменные успешно обновлены."})
        else:
            return jsonify({"message": "У вас нет прав для изменения переменных."})
    except ValueError:
        return jsonify({"message": "Admin ID должен быть числом."})
    # Заполнение таблицы данными пользователей
# Заполнение таблицы данными пользователей
@app.route('/list_users')
def list_users():
    users = users_db.get_all_users()  # Получаем всех пользователей из базы данных
    if not users:
        return "<p>Нет пользователей в базе данных.</p>"

    # Начало таблицы
    user_table = """
    <div class="table-container">
    <h2>Список пользователей:</h2>
    <table class="table table-striped" style="border: 1px solid black; border-collapse: collapse;">
        <thead>
            <tr>
                <th style="border: 1px solid black;">Имя пользователя</th>
                <th style="border: 1px solid black;">Chat ID</th>
                <th style="border: 1px solid black;">Дата подписки</th>
                <th style="border: 1px solid black;">Оплачена ли подписка</th>
                <th style="border: 1px solid black;">Повторных оплат</th>
            </tr>
        </thead>
        <tbody>
    """

    # Заполнение таблицы данными пользователей
    for user in users:
        user_table += f"""
        <tr>
            <td style="border: 1px solid black;">{user['username']}</td>
            <td style="border: 1px solid black;">{user['chat_id']}</td>
            <td style="border: 1px solid black;">{user['subscription_date']}</td>
            <td style="border: 1px solid black;">{user['is_active']}</td>
            <td style="border: 1px solid black;">{user['repeat_subscription']}</td>
        </tr>
        """

    # Закрытие таблицы
    user_table += """
        </tbody>
    </table>
    </div>
    """

    return user_table




@app.route('/list_channel_members')
def list_channel_members():
    members = users_db.display_users()  # Получаем участников канала
    if not members:
        return "Нет участников в канале."
    
    member_list = "<h2>Список участников канала:</h2><ul class='list-group'>"
    for member in members:
        member_list += f"<li class='list-group-item'>{member}</li>"  # Предполагается, что member - это строка с именем участника
    member_list += "</ul>"
    
    return member_list

if __name__ == '__main__':
    app.run(debug=True)
