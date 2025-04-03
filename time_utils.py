from datetime import datetime, timedelta
import pytz

def get_current_time():
    """Получить текущее время в UTC+3.00"""
    utc_now = datetime.now(pytz.UTC)
    moscow_tz = pytz.timezone('Europe/Moscow')  # Москва находится в UTC+3
    return utc_now.astimezone(moscow_tz)

def format_datetime(dt):
    """Форматировать datetime в строку с учетом UTC+3.00"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    moscow_tz = pytz.timezone('Europe/Moscow')
    return dt.astimezone(moscow_tz).strftime("%d.%m.%Y %H:%M:%S") 