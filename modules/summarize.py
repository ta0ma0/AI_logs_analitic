import os
import time
import logging
import settings.logger_config
from string import Template
from llama_cpp import Llama
from dotenv import load_dotenv
from settings.prompts import summarisation
from modules.gpu_test import check_gpu

PROJECT_ROOT = os.getenv("PROJECT_ROOT")
AI_RESULT_FILE = os.path.join(PROJECT_ROOT, "data", "reports", "ai_result_llama.txt")
AI_SUMMARY_FILE = os.path.join(PROJECT_ROOT, "data", "reports", "ai_summary.md")


load_dotenv()

# Settings from .env
ENCODING = os.getenv("ENCODING", "UTF-8")  # Encode report
N_GPU = os.getenv("N_GPU", 4)
logging.info(f'Setup n_gpu_layers = {N_GPU}')

def read_reports(AI_RESULT_FILE):
    with open(AI_RESULT_FILE, 'r', encoding='utf-8') as report_file:
        report_text = report_file.read()
    return report_text


def summarisation_report():
    report_text = read_reports(AI_RESULT_FILE)
    prompt = Template(summarisation).substitute(report=report_text)
    N_GPU = check_gpu()


    llm = Llama(
        model_path="/home/ruslan/.cache/lm-studio/models/bartowski/google_gemma-3-12b-it-GGUF/google_gemma-3-12b-it-Q4_K_S.gguf",
        # n_gpu_layers=N_GPU, 
        gpu_layers=N_GPU, 
        # seed=1337, 
        n_ctx=000, 
        use_mmap=True,
        verbose=False, # llama_cpp debug out (quiet)
)

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

def _write_results(report_text):
    report_text += "**Timestamp created:** " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
    try:
        with open(AI_SUMMARY_FILE, 'w', encoding='utf-8') as file:
            file.write(report_text + "\n---\n")
    except Exception as e:
        logging.error(f"!!! Error writing to file '{AI_SUMMARY_FILE}': {e}")


if __name__ == "__main__":
    logger_config.setup_logging()
    logging.info("Logging was setup")
    summarisation_report()