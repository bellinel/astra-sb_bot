# Telegram Bot для учета рабочего времени

Телеграм-бот для отслеживания рабочего времени сотрудников с геолокацией и интеграцией с Google Sheets.

## Функциональность

- Отслеживание времени прихода и ухода с работы
- Геолокация для определения адреса объекта
- Возможность перехода между объектами
- Формирование отчетов в Google Sheets
- Уведомления в групповой чат

## Установка

1. Клонируйте репозиторий:
```
git clone https://github.com/yourusername/telegram-work-time-bot.git
cd telegram-work-time-bot
```

2. Создайте виртуальное окружение и активируйте его:
```
python -m venv venv
# Для Windows
venv\Scripts\activate
# Для Linux/Mac
source venv/bin/activate
```

3. Установите зависимости:
```
pip install -r requirements.txt
```

4. Создайте файл `.env` со следующими переменными:
```
BOT_TOKEN=ваш_токен_бота
ADMIN_IDS=id_админов_через_запятую
DATABASE_PATH=db.sqlite3
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SPREADSHEET_ID=id_вашей_таблицы
GROUP_CHAT_ID=id_группового_чата
```

5. Настройте Google Sheets API:
   - Создайте проект в Google Cloud Console
   - Включите Google Sheets API
   - Создайте сервисный аккаунт и скачайте credentials.json
   - Предоставьте доступ к таблице для сервисного аккаунта

## Запуск

```
python bot.py
```

## Использование

1. Отправьте команду `/start` боту
2. Отправьте геолокацию для отметки прихода на работу
3. При уходе с работы отправьте геолокацию или нажмите "Закончить работу"
4. Для перехода на новый объект нажмите "Сменить объект"
5. Для формирования отчета используйте команду `/report`

## Структура проекта

- `bot.py` - основной файл бота
- `handler.py` - обработчики команд и сообщений
- `orm.py` - работа с базой данных
- `create_google_table.py` - работа с Google Sheets
- `geocoder.py` - сервис геокодирования
- `text_messages.py` - текстовые сообщения
- `keyboard.py` - клавиатуры для бота

## Лицензия

MIT 