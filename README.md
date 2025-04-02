# Telegram Bot с Google Sheets

Этот бот позволяет взаимодействовать с Google таблицами через Telegram.

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение: `python -m venv venv`
3. Активируйте виртуальное окружение:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Установите зависимости: `pip install -r requirements.txt`
5. Скопируйте `.env.example` в `.env` и заполните необходимые переменные окружения
6. Получите учетные данные Google API и сохраните их в файл `credentials.json`

## Настройка

1. Создайте бота в Telegram через @BotFather и получите токен
2. Создайте проект в Google Cloud Console и включите Google Sheets API
3. Создайте сервисный аккаунт и скачайте учетные данные в формате JSON
4. Заполните все необходимые переменные в файле `.env`

## Запуск

```bash
python bot.py
``` 