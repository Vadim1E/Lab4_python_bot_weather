"""
Этот модуль содержит класс WeatherAPI для взаимодействия с OpenWeatherMap API.

Классы:
    WeatherAPI: Класс для запроса текущей погоды и прогноза погоды по названию города.

Использование:
    from business_logic import WeatherAPI

    weather_api = WeatherAPI('your_api_key_here')
    current_weather = weather_api.get_weather_by_city('Moscow')
    forecast = weather_api.get_forecast_by_city('Moscow')
"""
import requests


class WeatherAPI:
    """
    Класс для запроса данных о погоде с использованием OpenWeatherMap API.

    Атрибуты:
        api_key (str): Ключ API для доступа к OpenWeatherMap.
        base_url (str): Базовый URL для запроса текущей погоды.
        forecast_url (str): Базовый URL для запроса прогноза погоды.

    Методы:
        __init__(self, api_key: str): Инициализирует экземпляр класса с указанным API ключом.
        get_weather_by_city(self, city: str) -> dict: Возвращает данные о текущей погоде для указанного города.
        get_forecast_by_city(self, city: str) -> dict: Возвращает прогноз погоды для указанного города.
    """

    def __init__(self, api_key: str):
        """
        Инициализирует экземпляр WeatherAPI с заданным ключом API.

        Аргументы:
            api_key (str): Ключ API для доступа к сервисам OpenWeatherMap.
        """
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"

    def get_weather_by_city(self, city: str) -> dict:
        """
        Получает данные о текущей погоде для заданного города.

        Аргументы:
            city (str): Название города, для которого запрашивается погода.

        Возвращает:
            dict: Словарь с данными о погоде, возвращенный OpenWeatherMap API.
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def get_forecast_by_city(self, city: str) -> dict:
        """
        Получает прогноз погоды на несколько дней для заданного города.

        Аргументы:
            city (str): Название города, для которого запрашивается прогноз погоды.

        Возвращает:
            dict: Словарь с прогнозом погоды, возвращенный OpenWeatherMap API.
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(self.forecast_url, params=params)
        return response.json()