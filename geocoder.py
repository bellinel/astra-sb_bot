from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import logging

# Настройка логгера
logger = logging.getLogger(__name__)


class GeocodingService:
    def __init__(self, user_agent="telegram_bot"):
        """
        Инициализирует сервис геокодирования
        :param user_agent: Идентификатор приложения для API
        """
        self.geolocator = Nominatim(user_agent=user_agent)
        
    async def get_address_by_coordinates(self, latitude, longitude, language="ru"):
        """
        Получает адрес по координатам
        :param latitude: Широта
        :param longitude: Долгота
        :param language: Язык ответа
        :return: Словарь с информацией о найденном адресе или None при ошибке
        """
        try:
            # Создаем строку координат
            coordinates = f"{latitude}, {longitude}"
            
            # Получаем информацию по координатам
            location = self.geolocator.reverse(coordinates, language=language, exactly_one=True)
            
            if not location:
                logger.warning(f"Адрес не найден для координат: {coordinates}")
                return None
            
            # Извлекаем данные из результата
            address = location.raw.get('address', {})
            
            # Подготавливаем структурированный ответ
            result = {
                'full_address': location.address,
                'city': address.get('city') or address.get('town') or address.get('village') or address.get('county', ''),
                'road': address.get('road', ''),
                'house_number': address.get('house_number', ''),
                'country': address.get('country', ''),
                'postal_code': address.get('postcode', ''),
                'state': address.get('state', ''),
                'raw': address
            }
            
            return result
            
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.error(f"Ошибка геокодирования: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return None


# Пример использования
async def test_geocoding():
    # Координаты центра Москвы
    lat, lon = 55.7558, 37.6173
    
    geocoder = GeocodingService()
    address = await geocoder.get_address_by_coordinates(lat, lon)
    
    if address:
        print(f"Полный адрес: {address['full_address']}")
        print(f"Город: {address['city']}")
        print(f"Улица: {address['road']}")
        if address['house_number']:
            print(f"Дом: {address['house_number']}")
        print(f"Страна: {address['country']}")
    else:
        print("Не удалось определить адрес")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_geocoding()) 