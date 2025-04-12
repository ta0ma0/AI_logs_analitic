import os
import sys
import time
import simple_web_server
import socketserver
import http.server
import telegram
import asyncio 
import subprocess
import markdown
import threading
import logger_config
import logging
import datetime
from llama_cpp import Llama
from simple_web_server import ReportHandler
from telegram_send import send as tg_send
from dotenv import load_dotenv
from telegram.constants import ParseMode
from notify import notification
from gpu_test import check_gpu
from datetime import datetime
from logger_config import setup_logging


load_dotenv()

# Settings from .env
REPORT_FILE = os.getenv('REPORT_FILE', "ai_result_llama.txt")
ENCODING = os.getenv("ENCODING", "UTF-8")  # Кодировка для отчета
PORT = int(os.getenv('PORT', 8000))  # Получаем порт из .env или используем 8000 по умолчанию
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "localhost.com")

# Report name and log fole name.
LOG_FILE = os.getenv("LOG_FILE", "daily_log_report.txt")
AI_RESULT_FILE = os.getenv("AI_RESULT_FILE", "ai_result_llama.txt")

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# GPU check
N_GPU = check_gpu() 


llm = Llama(
      model_path="/home/ruslan/.cache/lm-studio/models/bartowski/google_gemma-3-12b-it-GGUF/google_gemma-3-12b-it-Q4_K_S.gguf",
      n_gpu_layers=N_GPU, 
      # seed=1337, 
      n_ctx=14000, 
      use_mmap=True,
      verbose=False, # llama_cpp debug out (quiet)
)




# --- Logging setting up .env ---
LOG_LEVEL_CONSOLE_STR = os.getenv("LOG_LEVEL_CONSOLE", "INFO").upper()
LOG_LEVEL_FILE_STR = os.getenv("LOG_LEVEL_FILE", "DEBUG").upper()
LOG_FOLDER = os.getenv("LOG_FOLDER", "logs")
LOG_FILE_NAME_BASE = os.getenv("LOG_FILE_NAME_BASE", "app")
LOG_FORMAT = os.getenv("LOG_FORMAT", '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')
DATE_FORMAT = os.getenv("DATE_FORMAT", '%Y-%m-%d %H:%M:%S')

# Logging constants logging
LOG_LEVEL_CONSOLE = getattr(logging, LOG_LEVEL_CONSOLE_STR, logging.INFO)
LOG_LEVEL_FILE = getattr(logging, LOG_LEVEL_FILE_STR, logging.DEBUG)

# Create log file
LOG_FILE_NAME = f"{LOG_FILE_NAME_BASE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOG_FILE_PATH = os.path.join(LOG_FOLDER, LOG_FILE_NAME)


def log_analizator(chunk):
    """
    Llama linux log analitic
    """

    prompt = f"""
Q: Роль: Ты - эксперт по системным журналам Linux, обладающий глубокими знаниями о нормальном поведении системы Manjaro и распространенных признаках проблем.
Задача: Проанализируй предоставленный фрагмент системных логов. Твоя задача - выявить любые записи, которые могут указывать на:

    Сбои оборудования: Ошибки, связанные с дисками (например, SMART errors, I/O errors), памятью, процессором, сетевыми картами и другими аппаратными компонентами.
    Проблемы с программным обеспечением: Критические ошибки приложений, сбои служб, проблемы с зависимостями, ошибки ядра (kernel panic, oops).
    Подозрительную активность/потенциальные вторжения: Необычные попытки входа в систему (failed login attempts, особенно с неизвестных IP-адресов), изменения конфигурационных файлов, запуск подозрительных процессов, сетевая активность на необычных портах или с подозрительных IP-адресов, ошибки, связанные с безопасностью (например, SELinux/AppArmor denials, ошибки аутентификации).
    Аномалии в работе системы: Неожиданные перезагрузки, зависания, высокая загрузка ресурсов без видимой причины, необъяснимые ошибки в работе ранее стабильных служб.

Критерии анализа:

    Обращай внимание на: Сообщения об ошибках (error, critical, alert, emerg), предупреждения (warning), необычные паттерны, повторяющиеся ошибки, сообщения, связанные с безопасностью (security), сообщения ядра (kernel).
    Игнорируй: Информационные сообщения (info), отладочные сообщения (debug), записи о штатном запуске и остановке служб, плановые задачи (cron jobs), обычную сетевую активность, не связанную с подозрительными действиями.
    Учитывай контекст: Попробуй понять взаимосвязь между различными записями журнала. Последовательность ошибок может указывать на основную проблему.

Формат вывода:

    Если подозрительные записи обнаружены, выведи их, выделив наиболее важные части (например, время, служба, сообщение об ошибке).
    Для каждой подозрительной записи кратко объясни, почему она считается подозрительной и к какой категории проблем (сбой оборудования, ПО, вторжение, аномалия) она может относиться.
    Если обнаружено несколько связанных подозрительных записей, сгруппируй их и опиши общую потенциальную проблему.
    Если подозрительных записей не обнаружено, кратко сообщи об этом.

Дополнительные указания (опционально):

    Учитывай специфику системы Manjaro (например, используемые пакетные менеджеры, распространенные службы).
    Обращай внимание на сообщения, связанные с обновлениями системы, которые могли завершиться неудачно.

    {chunk}

    A:
    """ 

    answer = "Ошибка: Не удалось получить ответ от модели." # Значение по умолчанию

    try:
        output_dict = llm(
            prompt,
            max_tokens=2300, # Generate up to 2300 tokens
            # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question - возможно, стоит раскомментировать, если модель добавляет лишнее
            echo=False # Установите False, чтобы не включать промпт в ответ модели
                       # Если оставить True, нужно будет парсить ответ иначе
        ) # Generate a completion


        # Извлекаем текст ответа из словаря
        if output_dict and "choices" in output_dict and len(output_dict["choices"]) > 0 and "text" in output_dict["choices"][0]:
            answer = output_dict["choices"][0]["text"].strip() # Получаем текст и убираем лишние пробелы по краям
        else:
            logging.error(f"Wrong LLM answer {output_dict}")
            answer = "Error: wrong format anser from  LLM."


    except Exception as e:
        logging.critical(f"!!! Unexpected error {e}")
        return None 

    print("--- AI Analysis Result ---")
    print(answer)
    print("------------------------")

    _write_results(answer)
    return answer


def chankinizator(log):
    chunk_size = 200
    try:
        with open(log, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"!!! Ошибка: Лог-файл '{log}' не найден.")
        logging.error(f"Log file not found {log}")
        return [] # Возвращаем пустой итератор

    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i + chunk_size]
        yield ''.join(chunk)

def _write_results(report_text): # Функция теперь принимает строку
    report_text += "**Время создания:** " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
    try:
        with open(AI_RESULT_FILE, 'a', encoding='utf-8') as file:
            file.write(report_text + "\n---\n") # Добавляем разделитель между отчетами
    except Exception as e:
        print(f"!!! Ошибка при записи в файл '{AI_RESULT_FILE}': {e}")


class WebReportHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = REPORT_FILE
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def run_server(directory="."):
    """Запускает простой веб-сервер."""
    os.chdir(directory)
    httpd = socketserver.TCPServer((SERVER_ADDRESS, PORT), WebReportHandler)
    print(f"Сервер запущен на http://{SERVER_ADDRESS}:{PORT}/")
    httpd.serve_forever()
    print("Сервер остановлен.")

def open_browser_as_user(url, username):
    """Пытается открыть URL в новой вкладке существующего Firefox от имени пользователя."""
    display = os.environ.get('DISPLAY')
    if display:
        try:
            subprocess.run(
                ["su", "-", username, "-c", f"export DISPLAY='{display}'; chromium -new-tab '{url}'"],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Попытка открыть новую вкладку в Firefox от имени пользователя {username} с URL: {url} (DISPLAY={display})")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при попытке открыть новую вкладку в Firefox от имени пользователя {username}: {e}")
            print(f"Stdoutput: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            # Если не удалось открыть новую вкладку, можно попробовать запустить новый экземпляр (менее предпочтительно)
            try:
                subprocess.run(
                    ["su", "-", username, "-c", f"export DISPLAY='{display}'; chromium '{url}'"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"Запущен новый экземпляр Firefox от имени пользователя {username} с URL: {url} (DISPLAY={display})")
            except subprocess.CalledProcessError as e2:
                print(f"Ошибка при запуске нового экземпляра Firefox от имени пользователя {username}: {e2}")
                print(f"Stdoutput: {e2.stdout}")
                print(f"Stderr: {e2.stderr}")
        except FileNotFoundError:
            print(f"Ошибка: Команда 'su' или 'firefox' не найдена.")
    else:
        print("Предупреждение: Переменная DISPLAY не установлена. Невозможно запустить Firefox.")

url = '/home/ruslan/Develop/LinuxTools/AI_logs_analitic/ai_result_llama.txt'

async def main():
    await tg_send("Запущен анализ логов")
    # Сбор логов
    subprocess.run(['./collect_logs.sh'])
    logging.info('start logs collection - journalctl')

    log_name = LOG_FILE
    print(f"Starting log analysis from '{log_name}'...")
    analysis_count = 0
    # Очищаем файл с результатами перед новым анализом
    with open(AI_RESULT_FILE, 'w', encoding='utf-8') as f:
        pass
    logging.info('clened old reports')

    for chunk in chankinizator(log_name):
        if not chunk.strip(): # Пропускаем пустые чанки
            continue
        analysis_count += 1
        print(f"\n--- Analyzing Chunk {analysis_count} ---")
        logging.info(f'start analizing Chunk {analysis_count}')
        log_analizator(chunk)

    print(f"\nLog analysis finished. Results saved to '{AI_RESULT_FILE}'.")
    logging.info(f'report created {AI_RESULT_FILE}')

    
    open_browser_as_user(url, username)
    logging.info('browser opened')
    # 3. Отправка сообщения в Telegram
    if BOT_TOKEN and CHAT_ID:
        telegram_message = "Отчет об анализе логов готов:"
        await tg_send(telegram_message, report_url)
        logging.info('Sended nitification in Telegram')
        print("Сообщение отправлено в Telegram.")
    else:
        print("Предупреждение: BOT_TOKEN или CHAT_ID не найдены. Сообщение в Telegram не отправлено.")
        logging.error("CHAT_ID or BOT_TOKEN can't finded")

if __name__ == "__main__":
    setup_logging()
    logging.info("Logging was setup")
    asyncio.run(main())
    logging.info("Analazer was finally end working")
    print("Выход из основной программы.")