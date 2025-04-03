import os
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv
from typing import Union, List, Dict
import warnings

# Отключаем предупреждение о file_cache
warnings.filterwarnings('ignore', message='file_cache is unavailable when using oauth2client >= 4.0.0')

# Загружаем переменные окружения
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = "1D4X1T3_aP4kea-m7r0EYb-IViZL0FfXfaReMPSutTho"  # Используем ID из переменных окружения
SHEET_NAME = 'Лист1'  # Имя листа на русском
RANGE_NAME = f'{SHEET_NAME}!A:H'  # Диапазон для записи (8 колонок)

def get_google_sheets_service():
    """Создание сервиса для работы с Google Sheets"""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(f"Файл учетных данных не найден: {CREDENTIALS_FILE}")
            
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
        return service
    except Exception as e:
        raise Exception(f"Ошибка при создании сервиса Google Sheets: {str(e)}")

def format_worker_data(worker_data: Union[List, Dict]) -> List:
    """Форматирует данные работника в список для записи"""
    current_date = datetime.now()
    record_date = current_date.strftime("%Y-%m-%d")  # Дата записи (только дата без времени)
    
    if hasattr(worker_data, '__table__'):  # Проверка на SQLAlchemy модель
        return [
            record_date,  # Дата записи первым полем
            str(getattr(worker_data, 'user_id', '')),
            str(getattr(worker_data, 'user_name', '')),
            str(getattr(worker_data, 'start_address', '')),
            getattr(worker_data, 'time_to_start_work', current_date).strftime("%Y-%m-%d %H:%M:%S"),
            str(getattr(worker_data, 'left_address', '')),
            getattr(worker_data, 'time_to_left_work', current_date).strftime("%Y-%m-%d %H:%M:%S"),
            str(getattr(worker_data, 'work_time', ''))
        ]
    elif isinstance(worker_data, dict):
        return [
            record_date,  # Дата записи первым полем
            str(worker_data.get('user_id', '')),
            str(worker_data.get('user_name', '')),
            str(worker_data.get('start_address', '')),
            worker_data.get('time_to_start_work', current_date).strftime("%Y-%m-%d %H:%M:%S"),
            str(worker_data.get('left_address', '')),
            worker_data.get('time_to_left_work', current_date).strftime("%Y-%m-%d %H:%M:%S"),
            str(worker_data.get('work_time', ''))
        ]
    else:
        return [
            record_date,  # Дата записи первым полем
            str(worker_data[0]) if len(worker_data) > 0 else '',
            str(worker_data[1]) if len(worker_data) > 1 else '',
            str(worker_data[2]) if len(worker_data) > 2 else '',
            (worker_data[3] if len(worker_data) > 3 else current_date).strftime("%Y-%m-%d %H:%M:%S"),
            str(worker_data[4]) if len(worker_data) > 4 else '',
            (worker_data[5] if len(worker_data) > 5 else current_date).strftime("%Y-%m-%d %H:%M:%S"),
            str(worker_data[6]) if len(worker_data) > 6 else ''
        ]

async def write_to_sheet(worker_data: Union[List, Dict]):
    """Запись данных в существующую таблицу"""
    try:
        print(f"Начинаем запись в таблицу. ID таблицы: {SPREADSHEET_ID}")
        print(f"Используем файл учетных данных: {CREDENTIALS_FILE}")
        
        service = get_google_sheets_service()
        print("Сервис Google Sheets успешно создан")
        
        sheets = service.spreadsheets()
        print("Получаем текущие данные таблицы...")

        # Получаем текущие данные таблицы
        result = sheets.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        print(f"Получено {len(values)} строк из таблицы")
        
        # Если таблица пустая, добавляем заголовки
        if not values:
            headers = [
                ['Дата записи',
                 'ID', 'Имя работника', 'Адрес начала работы', 
                 'Время начала работы', 'Адрес окончания работы',
                 'Время окончания работы', 'Время работы']
            ]
            sheets.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'{SHEET_NAME}!A1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()

        # Форматируем данные работников
        if isinstance(worker_data, list) and all(hasattr(w, '__table__') for w in worker_data):
            # Если это список SQLAlchemy моделей
            row_data = [format_worker_data(worker) for worker in worker_data]
        else:
            # Если это одиночный объект
            row_data = [format_worker_data(worker_data)]

        # Определяем следующую пустую строку
        next_row = len(values) + 1 if values else 2
        
        # Записываем данные
        result = sheets.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A{next_row}',
            valueInputOption='RAW',
            body={'values': row_data}
        ).execute()

        # Формируем ссылку на таблицу
        sheet_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}'
        print(f"Данные успешно записаны в таблицу. Ссылка: {sheet_url}")
        return {
            'success': True,
            'url': sheet_url,
            'message': f'Данные успешно записаны в таблицу. Ссылка: {sheet_url}'
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Произошла ошибка при записи в таблицу'
        }
