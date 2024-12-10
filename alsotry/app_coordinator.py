from telegram import Update
from telegram.ext import Application, ContextTypes
import logging
from data_storage import DataStorage
from business_logic import WeatherAPI
from user_interface import WeatherBotUI

"""
Этот модуль содержит класс WeatherBotCoordinator для координации работы телеграм-бота, 
который предоставляет информацию о погоде, используя OpenWeatherMap API.

Классы:
    WeatherBotCoordinator: Класс для управления взаимодействием с пользователем через телеграм-бота.

Использование:
    Создайте экземпляр WeatherBotCoordinator, передав токен бота и ключ API погоды, и вызовите метод run().

Пример:
    if __name__ == "__main__":
        token = 'your_telegram_bot_token'
        weather_api_key = 'your_openweathermap_api_key'
        bot_coordinator = WeatherBotCoordinator(token, weather_api_key)
        bot_coordinator.run()
"""


class WeatherBotCoordinator:
    """
    Класс для управления взаимодействием с пользователем через телеграм-бота, предоставляя информацию о погоде.

    Методы:
        __init__(self, token: str, weather_api_key: str): Инициализирует бота с заданным токеном и ключом API погоды.
        handle_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обрабатывает запросы истории погоды пользователя.
        handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обрабатывает входящие сообщения и предоставляет текущую погоду.
        handle_forecast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обрабатывает запросы прогноза погоды.
        run(self): Запускает бота для обработки сообщений.
    
    Использует:
        - DataStorage для хранения истории запросов пользователей.
        - WeatherAPI для получения данных о погоде и прогноза погоды.
        - WeatherBotUI для управления пользовательским интерфейсом и взаимодействием с телеграм-ботом.
    """
    def __init__(self, token: str, weather_api_key: str):
        """
        Инициализирует экземпляр WeatherBotCoordinator.

        Параметры:
            token (str): Токен телеграм-бота.
            weather_api_key (str): Ключ API для доступа к данным OpenWeatherMap.
        """

        # Set up logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        # Initialize the bot and modules
        self.application = Application.builder().token(token).build()
        self.data_storage = DataStorage()
        self.weather_api = WeatherAPI(weather_api_key)
        self.ui = WeatherBotUI(self.application)

        # Attach handlers to the UI
        self.application.bot_data['history_handler'] = self.handle_history
        self.application.bot_data['message_handler'] = self.handle_message
        self.application.bot_data['forecast_handler'] = self.handle_forecast

    async def handle_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обрабатывает запрос истории погоды пользователя.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.
        
        Отправляет пользователю его историю запросов погоды или сообщение об их отсутствии.
        """
        user_id = update.effective_user.id
        history = self.data_storage.get_user_history(user_id)
        if not history:
            await update.message.reply_text('Your history is empty!')
        else:
            messages = []
            for entry in history:
                city = entry['city']
                weather = entry['weather']
                description = weather.get('weather', [{}])[0].get('description', 'No description')
                temp = weather.get('main', {}).get('temp', 'No temperature data')
                messages.append(f'City: {city}, Description: {description}, Temp: {temp}°C')
            await update.message.reply_text("\n".join(messages))

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обрабатывает входящие текстовые сообщения пользователей и предоставляет текущую погоду для указанного города.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.

        Анализирует текст сообщения как название города, запрашивает погоду и отвечает пользователю
        текущими данными погоды или сообщением об ошибке, если данные не найдены.
        """
        text = update.message.text
        user_id = update.effective_user.id

        # Fetch the weather
        weather = self.weather_api.get_weather_by_city(text)
        
        if weather.get("cod") != 200:
            await update.message.reply_text('Failed to get weather data. Please check the city name.')
            return
        
        description = weather['weather'][0]['description']
        temperature = weather['main']['temp']

        # Save the request to the history
        self.data_storage.save_weather_request(user_id, text, weather)

        # Respond to the user
        await update.message.reply_text(
            f"Weather in {text}:\n"
            f"{description.capitalize()}\n"
            f"Temperature: {temperature}°C\n"
        )

    async def handle_forecast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обрабатывает команды прогноза погоды, предоставляя прогноз на несколько дней для указанного города.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.

        Принимает текст команды, извлекает название города и отправляет пользователю прогноз погоды
        на ближайшие дни или сообщение об ошибке, если данные не найдены.
        """
        command_parts = update.message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await update.message.reply_text('Please provide a city name, e.g., /forecast Moscow')
            return
        city = command_parts[1]

        # Fetch the forecast
        forecast_data = self.weather_api.get_forecast_by_city(city)

        if forecast_data.get("cod") != "200":
            await update.message.reply_text('Failed to get forecast data. Please check the city name.')
            return

        forecast_list = forecast_data.get('list', [])
        messages = [f"Weather forecast for {city}:"]
        for forecast in forecast_list[:5]:  # Limit to 5 forecasts for brevity
            dt_txt = forecast.get('dt_txt', 'N/A')
            description = forecast['weather'][0]['description']
            temperature = forecast['main']['temp']
            messages.append(f"{dt_txt}: {description.capitalize()}, Temp: {temperature}°C")

        await update.message.reply_text("\n".join(messages))

    def run(self):
        """
        Запускает бота для обработки сообщений в режиме опроса.

        Инициирует бесконечный цикл обработки сообщений от телеграм-бота, используя 
        асинхронный ввод-вывод для обработки входящих обновлений.
        """
        self.application.run_polling()

if __name__ == "__main__":
    """
    Точка входа в программу. Создаёт и запускает бота с использованием токена и ключа API,
    указанных в переменных token и weather_api_key.
    """
    token = '8135019350:AAHj0wZ4v3P6uyPwuIDdwMLc1W6J1N0t8lU'
    weather_api_key = '86fb084491026ae755b76e8bfb4355a3'
    bot_coordinator = WeatherBotCoordinator(token, weather_api_key)
    bot_coordinator.run()


