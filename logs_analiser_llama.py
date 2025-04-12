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
from prompts import prompt_en, prompt_ru, prompt_ua, summarisation



load_dotenv()

# Settings from .env
REPORT_FILE = os.getenv('REPORT_FILE', "ai_result_llama.txt")
ENCODING = os.getenv("ENCODING", "UTF-8")  # Encode report
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

CHUNK_SIZE = os.getenv("CHUNK_SIZE", 150)




llm = Llama(
      model_path="/home/ruslan/.cache/lm-studio/models/bartowski/google_gemma-3-12b-it-GGUF/google_gemma-3-12b-it-Q4_K_S.gguf",
      n_gpu_layers=N_GPU, 
      # seed=1337, 
      n_ctx=17000, 
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

    chunk_size = CHUNK_SIZE
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

    
    # 3. Sending to Telegram
    if BOT_TOKEN and CHAT_ID:
        telegram_message = f"Отчет об анализе логов готов. Имя файла: {AI_RESULT_FILE}"
        await tg_send(telegram_message)
        logging.info('Sended nitification in Telegram')
    else:
        logging.error("CHAT_ID or BOT_TOKEN can't finded")

if __name__ == "__main__":
    setup_logging()
    logging.info("Logging was setup")
    asyncio.run(main())
    cleaning_logs(LOG_FOLDER, 30)
    logging.info("Analazer was finally end working")