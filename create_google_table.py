import os
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv
from typing import Union, List, Dict
import warnings
from time_utils import get_current_time, format_datetime
import pytz

# Отключаем предупреждение о file_cache
warnings.filterwarnings('ignore', message='file_cache is unavailable when using oauth2client >= 4.0.0')

# Загружаем переменные окружения
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')  # Используем ID из переменных окружения
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
    current_date = get_current_time()
    record_date = current_date.strftime("%Y-%m-%d")  # Дата записи (только дата без времени)
    
    def format_time_for_sheets(dt):
        """Форматирует время для Google Sheets с учетом часового пояса"""
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        moscow_tz = pytz.timezone('Europe/Moscow')
        return dt.astimezone(moscow_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    if hasattr(worker_data, '__table__'):  # Проверка на SQLAlchemy модель
        return [
            record_date,  # Дата записи первым полем
            str(getattr(worker_data, 'user_id', '')),
            str(getattr(worker_data, 'user_name', '')),
            str(getattr(worker_data, 'start_address', '')),
            format_time_for_sheets(getattr(worker_data, 'time_to_start_work', current_date)),
            str(getattr(worker_data, 'left_address', '')),
            format_time_for_sheets(getattr(worker_data, 'time_to_left_work', current_date)),
            str(getattr(worker_data, 'work_time', ''))
        ]
    elif isinstance(worker_data, dict):
        return [
            record_date,  # Дата записи первым полем
            str(worker_data.get('user_id', '')),
            str(worker_data.get('user_name', '')),
            str(worker_data.get('start_address', '')),
            format_time_for_sheets(worker_data.get('time_to_start_work', current_date)),
            str(worker_data.get('left_address', '')),
            format_time_for_sheets(worker_data.get('time_to_left_work', current_date)),
            str(worker_data.get('work_time', ''))
        ]
    else:
        return [
            record_date,  # Дата записи первым полем
            str(worker_data[0]) if len(worker_data) > 0 else '',
            str(worker_data[1]) if len(worker_data) > 1 else '',
            str(worker_data[2]) if len(worker_data) > 2 else '',
            format_time_for_sheets(worker_data[3] if len(worker_data) > 3 else current_date),
            str(worker_data[4]) if len(worker_data) > 4 else '',
            format_time_for_sheets(worker_data[5] if len(worker_data) > 5 else current_date),
            str(worker_data[6]) if len(worker_data) > 6 else ''
        ]

async def write_to_sheet(worker_data: Union[List, Dict]):
    """Запись данных в существующую таблицу"""
    try:
        print(f"[DEBUG] Начинаем запись в таблицу")
        print(f"[DEBUG] ID таблицы: {SPREADSHEET_ID}")
        print(f"[DEBUG] Файл учетных данных: {CREDENTIALS_FILE}")
        print(f"[DEBUG] Тип входных данных: {type(worker_data)}")
        
        service = get_google_sheets_service()
        print("[DEBUG] Сервис Google Sheets успешно создан")
        
        sheets = service.spreadsheets()
        print("[DEBUG] Получаем текущие данные таблицы...")

        # Получаем текущие данные таблицы
        result = sheets.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        print(f"[DEBUG] Результат получения данных: {result}")
        
        values = result.get('values', [])
        print(f"[DEBUG] Получено {len(values)} строк из таблицы")
        
        # Если таблица пустая, добавляем заголовки
        if not values:
            print("[DEBUG] Таблица пустая, добавляем заголовки")
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
        print(f"[DEBUG] Форматируем данные работника: {worker_data}")
        if isinstance(worker_data, list) and all(hasattr(w, '__table__') for w in worker_data):
            # Если это список SQLAlchemy моделей
            row_data = [format_worker_data(worker) for worker in worker_data]
        else:
            # Если это одиночный объект
            row_data = [format_worker_data(worker_data)]
        print(f"[DEBUG] Отформатированные данные: {row_data}")

        # Определяем следующую пустую строку
        next_row = len(values) + 1 if values else 2
        print(f"[DEBUG] Следующая строка для записи: {next_row}")
        
        # Записываем данные
        result = sheets.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A{next_row}',
            valueInputOption='RAW',
            body={'values': row_data}
        ).execute()
        print(f"[DEBUG] Результат записи: {result}")

        # Формируем ссылку на таблицу
        sheet_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}'
        print(f"[DEBUG] Данные успешно записаны в таблицу. Ссылка: {sheet_url}")
        return {
            'success': True,
            'url': sheet_url,
            'message': f'Данные успешно записаны в таблицу. Ссылка: {sheet_url}'
        }

    except Exception as e:
        print(f"[ERROR] Произошла ошибка при записи в таблицу: {str(e)}")
        print(f"[ERROR] Тип ошибки: {type(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Произошла ошибка при записи в таблицу'
        }
