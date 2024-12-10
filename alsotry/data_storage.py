"""
Этот модуль предоставляет класс для управления постоянным хранением данных о запросах погоды.

Классы:
    DataStorage: Класс для управления загрузкой, сохранением и доступом к данным о погоде.

Использование:
    from data_storage import DataStorage
    storage = DataStorage('weather_data.json')
    storage.save_weather_request(1, 'Лондон', {'temp': 70, 'description': 'солнечно'})
    history = storage.get_user_history(1)
"""
import json
from typing import Any, Dict

class DataStorage:
    """
    Класс для управления постоянным хранением данных о погоде в JSON-файле.

    Атрибуты:
        filename (str): Имя файла, в котором хранятся данные.
        data (dict): Внутреннее хранилище данных о погоде, загруженное из JSON-файла.

    Методы:
        __init__(self, filename='data.json'): Инициализирует экземпляр DataStorage.
        _load_data(self): Загружает данные о погоде из указанного JSON-файла.
        _save_data(self): Сохраняет текущие данные в памяти в JSON-файл.
        save_weather_request(self, user_id: int, city: str, weather: Dict[str, Any]): 
            Сохраняет запрос погоды для пользователя.
        get_user_history(self, user_id: int): Получает историю запросов погоды пользователя.
    """

    def __init__(self, filename: str = 'data.json'):
        """
        Инициализирует экземпляр DataStorage, загружая данные из указанного JSON-файла.

        Аргументы:
            filename (str): Имя файла JSON, в котором хранятся данные о погоде. 
                            По умолчанию 'data.json'.
        """
        self.filename = filename
        self._load_data()

    def _load_data(self):
        """
        Загружает данные о погоде из файла JSON. Если файл не существует, инициализирует
        пустой словарь данных.
        """
        try:
            with open(self.filename, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}

    def _save_data(self):
        """
        Сохраняет текущий словарь данных в памяти в файл JSON с форматированием для удобочитаемости.
        """
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def save_weather_request(self, user_id: int, city: str, weather: Dict[str, Any]):
        """
        Сохраняет запрос погоды для указанного пользователя.

        Аргументы:
            user_id (int): Идентификатор пользователя, делающего запрос.
            city (str): Название города, для которого сохраняются данные о погоде.
            weather (Dict[str, Any]): Словарь с данными о погоде.

        Этот метод добавляет запрос погоды в список запросов пользователя и сохраняет
        обновлённые данные в файл JSON.
        """
        if user_id not in self.data:
            self.data[user_id] = []
        self.data[user_id].append({
            'city': city,
            'weather': weather
        })
        self._save_data()

    def get_user_history(self, user_id: int):
        """
        Получает историю запросов погоды указанного пользователя.

        Аргументы:
            user_id (int): Идентификатор пользователя, чью историю запросов нужно получить.

        Возвращает:
            list: Список словарей, каждый из которых содержит 'city' и 'weather' для каждого запроса
            запроса, сделанного пользователем. Возвращает пустой список, если для пользователя нет истории запросов.
        """
        return self.data.get(user_id, [])