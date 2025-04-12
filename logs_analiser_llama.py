import os
import time
import asyncio 
import subprocess
import threading
import logger_config
import logging
import datetime
import cleaning_logs
from string import Template
from llama_cpp import Llama
from telegram_send import send as tg_send
from dotenv import load_dotenv
from gpu_test import check_gpu
from logger_config import setup_logging
from cleaning_logs import delete_old_files
from prompts import prompt_en, prompt_ru, prompt_ua



load_dotenv()

# Settings from .env
REPORT_FILE = os.getenv('REPORT_FILE', "ai_result_llama.txt")
ENCODING = os.getenv("ENCODING", "UTF-8")  # Кодировка для отчета
PORT = int(os.getenv('PORT', 8000))  # Получаем порт из .env или используем 8000 по умолчанию
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "localhost.com")

# Report name and log fole name.
LOG_FOLDER = os.getenv("LOG_FOLDER", "logs")
LOG_FILE = os.getenv("LOG_FILE", "daily_log_report.txt")
AI_RESULT_FILE = os.getenv("AI_RESULT_FILE", "ai_result_llama.txt")

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# GPU check
N_GPU = check_gpu()
logging.info(f'Setup n_gpu_layers = {N_GPU}')



llm = Llama(
      model_path="/home/ruslan/.cache/lm-studio/models/bartowski/google_gemma-3-12b-it-GGUF/google_gemma-3-12b-it-Q4_K_S.gguf",
      n_gpu_layers=N_GPU, 
      # seed=1337, 
      n_ctx=14000, 
      use_mmap=True,
      verbose=False, # llama_cpp debug out (quiet)
)


def log_analizator(chunk):
    """
    Llama linux log analitic
    """
    prompt = os.getenv('PROMPT_LANGUAGE', 'RU')
    if prompt == 'EN':
        prompt = Template(prompt_en).substitute(chunk=chunk)
        logging.info(f"Chose language English")
        print(chunk)
    elif prompt == 'UA':
        prompt = Template(prompt_ua).substitute(chunk=chunk)
        logging.info(f"Chose language Ukrainian")
        print(chunk)
    else:
        prompt = Template(prompt_ru).substitute(chunk=chunk)
        logging.info(f"Chose language Russian")
        print(chunk)

    answer = "Ошибка: Не удалось получить ответ от модели." # Значение по умолчанию

    try:
        output_dict = llm(
            prompt,
            max_tokens=2300, # Generate up to 2300 tokens
            # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question - возможно, стоит раскомментировать, если модель добавляет лишнее
            echo=False # Установите False, чтобы не включать промпт в ответ модели
                       # Если оставить True, нужно будет парсить ответ иначе
        ) # Generate a completion


        # Extract text answer from dict 
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
        logging.error(f"Log file not found {log}")
        return []

    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i + chunk_size]
        yield ''.join(chunk)

def _write_results(report_text):
    report_text += "**Время создания:** " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
    try:
        with open(AI_RESULT_FILE, 'a', encoding='utf-8') as file:
            file.write(report_text + "\n---\n")
    except Exception as e:
        logging.error(f"!!! Error writing to file '{AI_RESULT_FILE}': {e}")


async def main():
    await tg_send("Запущен анализ логов")
    # Сбор логов
    subprocess.run(['./collect_logs.sh'])
    logging.info('start logs collection - journalctl')

    log_name = LOG_FILE
    print(f"Starting log analysis from '{log_name}'...")
    analysis_count = 0
    # Cleaning old report
    with open(AI_RESULT_FILE, 'w', encoding='utf-8') as f:
        pass
    logging.info('clened old reports')

    for chunk in chankinizator(log_name):
        if not chunk.strip():
            continue
        analysis_count += 1
        print(f"\n--- Analyzing Chunk {analysis_count} ---")
        logging.info(f'start analizing Chunk {analysis_count}')
        log_analizator(chunk)

    print(f"\nLog analysis finished. Results saved to '{AI_RESULT_FILE}'.")
    logging.info(f'report created {AI_RESULT_FILE}')

    
    # 3. Отправка сообщения в Telegram
    if BOT_TOKEN and CHAT_ID:
        telegram_message = f"Отчет об анализе логов готов. Имя файла: {AI_RESULT_FILE}"
        await tg_send(telegram_message)
        logging.info('Sended nitification in Telegram')
        print("Сообщение отправлено в Telegram.")
    else:
        print("Предупреждение: BOT_TOKEN или CHAT_ID не найдены. Сообщение в Telegram не отправлено.")
        logging.error("CHAT_ID or BOT_TOKEN can't finded")

if __name__ == "__main__":
    setup_logging()
    logging.info("Logging was setup")
    asyncio.run(main())
    cleaning_logs(LOG_FOLDER, 30)
    logging.info("Analazer was finally end working")