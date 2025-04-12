import google.generativeai as genai
import os
import time
import simple_web_server
import socketserver
from simple_web_server import ReportHandler
from telegram_send import send


# Daily file log name

log_name = 'daily_log_report.txt'
ai_result_file = 'ai_result.txt'


# Configure the API key
genai.configure(api_key=os.environ['API_KEY'])  # Replace with your actual API key or set it as an environment variable

# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 900,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

def log_analizator(chunk):
    """
    Gemini linux log analitic
    """

    prompt = f"""
Роль: Ты - эксперт по системным журналам Linux, обладающий глубокими знаниями о нормальном поведении системы Manjaro и распространенных признаках проблем.
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
    """

    try:
        response = model.generate_content(prompt)
        response.resolve()
        result_text = response.text
        time.sleep(10)
    except Exception as e:
        print('!!!Unexpected error: f{e}')
        return None
    _write_results(result_text)
    return result_text


def chankinizator(log):
    chunk_size = 200
    with open(log, 'r') as file:
        lines = file.readlines()

    for chunk in [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]:
        yield ''.join(chunk)

def _write_results(report):
    with open(ai_result_file, 'a') as file:
        file.write(report)


for chunk in chankinizator(log_name):
    log_analizator(chunk)

analysis_count = 0
for chunk in chankinizator(log_name):
    if not chunk.strip(): # Пропускаем пустые чанки
        continue
    analysis_count += 1
    print(f"\n--- Analyzing Chunk {analysis_count} ---")
    log_analizator(chunk)
    # time.sleep(1) # Небольшая пауза, если нужно, но для локальной модели обычно не требуется

print(f"\nLog analysis finished. Results saved to '{ai_result_file}'.")

with socketserver.TCPServer(("", PORT), ReportHandler) as httpd:
        print(f"Веб-сервер запущен на порту {PORT}. Откройте в браузере: http://localhost:{PORT}")
        send(f"Создан отчет по системе, http://localhost:{PORT}")
        httpd.serve_forever()