import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- Настройки логирования из .env ---
LOG_LEVEL_CONSOLE_STR = os.getenv("LOG_LEVEL_CONSOLE", "INFO").upper()
LOG_LEVEL_FILE_STR = os.getenv("LOG_LEVEL_FILE", "DEBUG").upper()
LOG_FOLDER = os.getenv("LOG_FOLDER", "logs")
LOG_FILE_NAME_BASE = os.getenv("LOG_FILE_NAME_BASE", "app")
LOG_FORMAT = os.getenv("LOG_FORMAT", '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')
DATE_FORMAT = os.getenv("DATE_FORMAT", '%Y-%m-%d %H:%M:%S')

# Преобразуем строковые уровни логирования в константы logging
LOG_LEVEL_CONSOLE = getattr(logging, LOG_LEVEL_CONSOLE_STR, logging.INFO)
LOG_LEVEL_FILE = getattr(logging, LOG_LEVEL_FILE_STR, logging.DEBUG)

# Формируем имя файла лога
LOG_FILE_NAME = f"{LOG_FILE_NAME_BASE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOG_FILE_PATH = os.path.join(LOG_FOLDER, LOG_FILE_NAME)

def setup_logging():
    """Настраивает логирование в файл и консоль."""
    # Создаем папку для логов, если она не существует
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    # Получаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(min(LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE)) # Устанавливаем минимальный уровень для логгера

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Создаем обработчик для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL_CONSOLE)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Создаем обработчик для записи логов в файл
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

if __name__ == "__main__":
    setup_logging()
    logging.info("Логирование успешно настроено из logger_config.")

    def some_function_in_logger_config():
        logging.debug("Функция some_function_in_logger_config вызвана")
        try:
            result = 10 / 0
        except ZeroDivisionError:
            logging.error("Произошла ошибка деления на ноль в logger_config", exc_info=True)

    some_function_in_logger_config()