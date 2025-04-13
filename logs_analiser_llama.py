import os
import time
import asyncio 
import logging
import datetime
import threading
import subprocess
import cleaning_logs
import logger_config
from llama_cpp import Llama
from string import Template
from dotenv import load_dotenv
from gpu_test import check_gpu
from logger_config import setup_logging
from telegram_send import send as tg_send
from cleaning_logs import delete_old_files
from summarize import summarisation_report
from prompts import prompt_en, prompt_ru, prompt_ua, summarisation



load_dotenv()

# Settings from .env
REPORT_FILE = os.getenv('REPORT_FILE', "data/ai_result_llama.txt")
ENCODING = os.getenv("ENCODING", "UTF-8")  # Encode report

# Report name and log fole name.
LOG_FOLDER = os.getenv("LOG_FOLDER", "data/logs")
LOG_FILE = os.getenv("LOG_FILE", "data/daily_log_report.txt")
AI_RESULT_FILE = os.getenv("AI_RESULT_FILE", "data/ai_result_llama.txt")
AI_RESUME_FILE = os.getenv("AI_RESUME_FILE", "data/ai_summary.md")

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')



CHUNK_SIZE = os.getenv("CHUNK_SIZE", 150)

def log_analizator(chunk):

    """
    Llama linux log analitic
    """
    llm = Llama(
      model_path="/home/ruslan/.cache/lm-studio/models/bartowski/google_gemma-3-12b-it-GGUF/google_gemma-3-12b-it-Q4_K_S.gguf",
      n_gpu_layers=N_GPU, 
      # seed=1337, 
      n_ctx=17000, 
      use_mmap=True,
      verbose=False, # llama_cpp debug out (quiet)
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
            max_tokens=2300, # Generate up to 2300 tokens
            # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question - возможно, стоит раскомментировать, если модель добавляет лишнее
            echo=False # Setup False, for not prompt in answer
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
    time.sleep(10) # Waiting for nload model
    logging.info("Starting summarisation report")
    summarisation_report()

    # Sending to Telegram
    if BOT_TOKEN and CHAT_ID:
        telegram_message = f"Отчет об анализе логов готов. Имя файла: {AI_RESUME_FILE}"
        await tg_send(telegram_message)
        logging.info('Sended nitification in Telegram')
    else:
        logging.error("CHAT_ID or BOT_TOKEN can't found in .env file")

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    # Inicialisation
    setup_logging()
    logging.info("Logging was setup")

    # GPU check
    N_GPU = check_gpu()
    logging.info(f'Setup n_gpu_layers = {N_GPU}')

    # Main loop
    asyncio.run(main())

    # After work
    delete_old_files(LOG_FOLDER, 7)
    logging.info("Analazer was finally end working")
    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    total_exec_time = f"Total execution time: {format_timedelta(execution_time)}"
    logging.info(f"Execution time: {total_exec_time}")