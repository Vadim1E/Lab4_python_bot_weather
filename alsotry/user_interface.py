"""
Этот модуль содержит класс WeatherBotUI, который определяет пользовательский интерфейс для телеграм-бота,
предоставляющего информацию о погоде.

Классы:
    WeatherBotUI: Класс, управляющий пользовательским интерфейсом телеграм-бота.

Использование:
    Создайте экземпляр WeatherBotUI, передав ему объект Application от telegram.ext, и он автоматически
    настроит обработчики команд и сообщений.
"""
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


class WeatherBotUI:
    """
    Класс для настройки и управления пользовательским интерфейсом телеграм-бота, предоставляющего погодные услуги.

    Этот класс настраивает обработчики для различных команд и текстовых сообщений, которые бот может получать.

    Методы:
        __init__(self, application: Application): Инициализирует экземпляр класса с указанным объектом Application.
        _setup_handlers(self): Приватный метод для настройки обработчиков команд и сообщений.
        start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обработчик команды /start.
        help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обработчик команды /help.
        history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обработчик команды /history.
        forecast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обработчик команды /forecast.
        handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: Обработчик текстовых сообщений.
    """
    def __init__(self, application: Application):
        """
        Инициализирует экземпляр WeatherBotUI, настраивая обработчики команд и сообщений для телеграм-бота.

        Параметры:
            application (Application): Объект Application из telegram.ext, используемый для настройки бота.
        """
        self.application = application
        self._setup_handlers()

    def _setup_handlers(self):
        """
        Настраивает обработчики для команд и текстовых сообщений, добавляя их в приложение телеграм-бота.

        Этот метод настраивает обработчики для команд /start, /help, /history, /forecast и для обработки
        всех текстовых сообщений, которые не являются командами.
        """
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("history", self.history))
        self.application.add_handler(CommandHandler("forecast", self.forecast))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Отправляет приветственное сообщение пользователю в ответ на команду /start.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.

        Отправляет пользователю приветственное сообщение, предлагающее отправить название города для получения погоды.
        """
        user = update.effective_user
        await update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()}\! Welcome to the Weather Bot\.\n'
            'Send me a city name and I\'ll provide you with the current weather information\.\n'
            'You can also use /help to see more commands\.',
            reply_markup=ForceReply(selective=True))

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Отправляет пользователю сообщение с описанием доступных команд в ответ на команду /help.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.

        Отправляет пользователю список команд и их описания, помогая понять, как взаимодействовать с ботом.
        """
        await update.message.reply_text(
            '/start - Start the conversation\n'
            '/help - Show this help message\n'
            '/history - Show your past weather queries\n'
            '/forecast <city> - Get the weather forecast\n'
            'Just send a city name to get the weather information for that city\.')

    async def history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обрабатывает команду /history, показывая пользователю его историю запросов погоды.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.

        Вызывает обработчик истории из основного объекта бота, который выводит пользователю его историю запросов погоды.
        """
        await context.bot_data['history_handler'](update, context)

    async def forecast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обрабатывает команду /forecast, показывая прогноз погоды для указанного города.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.

        Пользователь должен указать город как часть команды (например, /forecast Moscow).
        Бот отправляет прогноз погоды для указанного города или сообщение об ошибке, если город не найден.
        """
        await context.bot_data['forecast_handler'](update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обрабатывает входящие текстовые сообщения, которые не являются командами, предполагая, что это названия городов.

        Параметры:
            update (Update): Объект Update от телеграм-бота, содержащий данные сообщения.
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения, содержащий дополнительные данные.

        Когда пользователь отправляет название города, бот запрашивает текущую погоду для этого города и отправляет
        информацию пользователю или сообщает об ошибке, если информацию получить не удалось.
        """
        await context.bot_data['message_handler'](update, context)