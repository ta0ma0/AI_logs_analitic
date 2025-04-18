import os
import time
import asyncio 
import logging
import datetime
import threading
import subprocess
import modules.cleaning_logs
import settings.logger_config
from llama_cpp import Llama
from string import Template
from dotenv import load_dotenv
from modules.gpu_test import check_gpu
from settings.logger_config import setup_logging
from modules.telegram_send import send as tg_send
from modules.cleaning_logs import delete_old_files
from modules.summarize import summarisation_report
from settings.prompts import prompt_en, prompt_ru, prompt_ua, summarisation



load_dotenv()

# Settings from .env
REPORT_FILE = os.getenv('REPORT_FILE', "data/ai_result_llama.txt")
ENCODING = os.getenv("ENCODING", "UTF-8")  # Encode report

# Report name and log fole name.
PROJECT_ROOT = os.getenv('PROJECT_ROOT')
AI_RESULT_FILE = os.path.join(PROJECT_ROOT, "data", "reports", "ai_result_llama.txt")
AI_SUMMARY_FILE = os.path.join(PROJECT_ROOT, "data", "reports", "ai_summary.md")
LOG_FOLDER = os.path.join(PROJECT_ROOT, "data/logs")
LOG_FILE = os.path.join(PROJECT_ROOT, "data", "daily_log_report.txt")
N_CTX = os.getenv(N_CTX, 15000)
LLM_VERBOSE = os.getenv(LLM_VERBOSE, False)

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

MODEL_PATH = os.path.join(PROJECT_ROOT, "models")


CHUNK_SIZE = os.getenv("CHUNK_SIZE", 250)
# Inicialisation
setup_logging()
logging.info("Logging was setup")
# N_GPU = check_gpu()
N_GPU = os.getenv("N_GPU", 4)
logging.info(f'Setup n_gpu_layers = {N_GPU}')

def create_directory_hierarchy():
    """
    Создает иерархию директорий 'data', 'data/logs' и 'data/reports'
    в текущей рабочей директории, если они не существуют.
    Если директории уже существуют, функция ничего не делает.
    """
    base_dir = "data"
    logs_dir = os.path.join(base_dir, "logs")
    reports_dir = os.path.join(base_dir, "reports")

    # Создаем корневую директорию 'data', если она не существует
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Создана директория: {base_dir}")
    else:
        print(f"Директория '{base_dir}' уже существует.")

    # Создаем директорию 'logs' внутри 'data', если она не существует
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Создана директория: {logs_dir}")
    else:
        print(f"Директория '{logs_dir}' уже существует.")

    # Создаем директорию 'reports' внутри 'data', если она не существует
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        print(f"Создана директория: {reports_dir}")
    else:
        print(f"Директория '{reports_dir}' уже существует.")

def log_analizator(chunk):

    """
    Llama linux log analitic
    """
    llm = Llama(
      model_path="/home/ruslan/.cache/lm-studio/models/bartowski/google_gemma-3-12b-it-GGUF/google_gemma-3-12b-it-Q4_K_S.gguf",
      n_gpu_layers=int(N_GPU),
      # seed=1337, 
      n_ctx=N_CTX, 
      use_mmap=False,
      verbose=LLM_VERBOSE, # llama_cpp debug out (quiet)
    )
    prompt = os.getenv('PROMPT_LANGUAGE', 'RU')

    if prompt == 'EN':
        prompt = Template(prompt_en).substitute(chunk=chunk)
    elif prompt == 'UA':
        prompt = Template(prompt_ua).substitute(chunk=chunk)
    else:
        prompt = Template(prompt_ru).substitute(chunk=chunk)

    answer = "Error, no answer from LLM" # Default anwer value

    try:
        output_dict = llm(
            prompt,
            max_tokens=1500, # Generate up to 2300 tokens
            # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question - возможно, стоит раскомментировать, если модель добавляет лишнее
            echo=False, # Setup False, for not prompt in answer
            temperature=0.7
        ) 
        
        # Extract text answer from dict 
        if output_dict and "choices" in output_dict and len(output_dict["choices"]) > 0 and "text" in output_dict["choices"][0]:
            answer = output_dict["choices"][0]["text"].strip()
        else:
            logging.error(f"Wrong LLM answer {output_dict}")
            answer = "Error: wrong format anser from  LLM."


    except Exception as e:
        logging.critical(f"!!! Unexpected error {e}")
        return None 

    # Writing AI analitic result to report file
    _write_results(answer)
    return answer


def chankinizator(log):

    chunk_size = int(CHUNK_SIZE)
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
    print(f"Current working directory: {os.getcwd()}")
    report_text += "**Timestamp created:** " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
    try:
        with open(AI_RESULT_FILE, 'a', encoding='utf-8') as file:
            file.write(report_text + "\n---\n")
    except Exception as e:
        logging.error(f"!!! Error writing to file '{AI_RESULT_FILE}': {e}")


def format_timedelta(delta):
    """
    Форматирует объект timedelta в строку вида ЧЧ:ММ:СС.
    """
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

async def main():
    start_time = datetime.datetime.now()
    await tg_send("Запущен анализ логов")
    # Сбор логов
    # subprocess.run(['./collect_logs.sh'])
    # logging.info('start logs collection - journalctl')

    log_name = LOG_FILE
    print(f"Starting log analysis from '{log_name}'...")
    analysis_count = 0
    # Cleaning old report
    with open(AI_RESULT_FILE, 'w', encoding='utf-8') as f:
        pass
    logging.info('cleaned old reports')
    # GPU check
    
    for chunk in chankinizator(log_name):
        if not chunk.strip():
            continue
        analysis_count += 1
        print(f"\n--- Analyzing Chunk {analysis_count} ---")
        # print(chunk)
        # chunk_string = f'"{chunk}"'
        # count_symbols = subprocess.run(['wc', chunk_string])
        # print(f"Count symbols: {count_symbols}")
        logging.info(f'start analizing Chunk {analysis_count}')
        log_analizator(chunk)

    print(f"\nLog analysis finished. Results saved to '{AI_RESULT_FILE}'.")
    logging.info(f'report created {AI_RESULT_FILE}')
    time.sleep(15) # Waiting for load model
    logging.info("Starting summarisation report")
    summarisation_report()

    # Sending to Telegram
    if BOT_TOKEN and CHAT_ID:
        telegram_message = f"Отчет об анализе логов готов. Имя файла: {AI_SUMMARY_FILE}"
        await tg_send(telegram_message)
        logging.info('Sended nitification in Telegram')
    else:
        logging.error("CHAT_ID or BOT_TOKEN can't found in .env file")

    return start_time

if __name__ == "__main__":
    create_directory_hierarchy()





    # Main loop
    start_time = asyncio.run(main())

    # After work
    delete_old_files(LOG_FOLDER, 7)
    logging.info("Analazer was finally end working")
    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    total_exec_time = f"Total execution time: {format_timedelta(execution_time)}"
    logging.info(f"Execution time: {total_exec_time}")