from string import Template

prompt_ru_template = Template("""
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

    $chunk

    A:
    """ 
)

prompt_en_template = Template("""
Q: Role: You are an expert in Linux system logs, possessing deep knowledge of the normal behavior of a Manjaro system and common signs of problems.
Task: Analyze the provided snippet of system logs. Your task is to identify any entries that might indicate:

    Hardware failures: Errors related to disks (e.g., SMART errors, I/O errors), memory, CPU, network cards, and other hardware components.
    Software issues: Critical application errors, service crashes, dependency problems, kernel errors (kernel panic, oops).
    Suspicious activity/potential intrusions: Unusual login attempts (failed login attempts, especially from unknown IP addresses), changes to configuration files, execution of suspicious processes, network activity on unusual ports or from suspicious IP addresses, security-related errors (e.g., SELinux/AppArmor denials, authentication failures).
    System anomalies: Unexpected reboots, freezes, high resource usage without apparent cause, unexplained errors in previously stable services.

Analysis Criteria:

    Pay attention to: Error messages (error, critical, alert, emerg), warnings, unusual patterns, recurring errors, security-related messages (security), kernel messages (kernel).
    Ignore: Informational messages (info), debugging messages (debug), records of normal service startup and shutdown, scheduled tasks (cron jobs), regular network activity unrelated to suspicious actions.
    Consider the context: Try to understand the relationship between different log entries. The sequence of errors might point to an underlying problem.

Output Format:

    If suspicious entries are found, output them, highlighting the most important parts (e.g., timestamp, service, error message).
    For each suspicious entry, briefly explain why it is considered suspicious and to which category of problems (hardware failure, software issue, intrusion, anomaly) it might belong.
    If several related suspicious entries are found, group them and describe the overall potential problem.
    If no suspicious entries are found, briefly state this.

Additional Instructions (optional):

    Consider the specifics of the Manjaro system (e.g., used package managers, common services).
    Pay attention to messages related to system updates that might have failed.
    
    $chunk

    A:
"""
)
prompt_ua_template = Template("""
Q: Роль: Ти - експерт з системних журналів Linux, що володіє глибокими знаннями про нормальну поведінку системи Manjaro та поширені ознаки проблем.
Завдання: Проаналізуй наданий фрагмент системних логів. Твоє завдання - виявити будь-які записи, які можуть вказувати на:

    Збої обладнання: Помилки, пов'язані з дисками (наприклад, SMART errors, I/O errors), пам'яттю, процесором, мережевими картами та іншими апаратними компонентами.
    Проблеми з програмним забезпеченням: Критичні помилки застосунків, збої служб, проблеми із залежностями, помилки ядра (kernel panic, oops).
    Підозрілу активність/потенційні вторгнення: Незвичайні спроби входу в систему (failed login attempts, особливо з невідомих IP-адрес), зміни конфігураційних файлів, запуск підозрілих процесів, мережева активність на незвичайних портах або з підозрілих IP-адрес, помилки, пов'язані з безпекою (наприклад, SELinux/AppArmor denials, помилки автентифікації).
    Аномалії в роботі системи: Неочікувані перезавантаження, зависання, високе завантаження ресурсів без видимої причини, незрозумілі помилки в роботі раніше стабільних служб.

Критерії аналізу:

    Звертай увагу на: Повідомлення про помилки (error, critical, alert, emerg), попередження (warning), незвичайні патерни, повторювані помилки, повідомлення, пов'язані з безпекою (security), повідомлення ядра (kernel).
    Ігноруй: Інформаційні повідомлення (info), налагоджувальні повідомлення (debug), записи про штатний запуск і зупинку служб, планові завдання (cron jobs), звичайну мережеву активність, не пов'язану з підозрілими діями.
    Враховуй контекст: Спробуй зрозуміти взаємозв'язок між різними записами журналу. Послідовність помилок може вказувати на основну проблему.

Формат виводу:

    Якщо підозрілі записи виявлено, виведи їх, виділивши найважливіші частини (наприклад, час, служба, повідомлення про помилку).
    Для кожного підозрілого запису коротко поясни, чому він вважається підозрілим і до якої категорії проблем (збій обладнання, ПЗ, вторгнення, аномалія) він може належати.
    Якщо виявлено кілька пов'язаних підозрілих записів, згрупуй їх та опиши загальну потенційну проблему.
    Якщо підозрілих записів не виявлено, коротко повідом про це.

Додаткові вказівки (необов'язково):

    Враховуй специфіку системи Manjaro (наприклад, використовувані пакетні менеджери, поширені служби).
    Звертай увагу на повідомлення, пов'язані з оновленнями системи, які могли завершитися невдало.
    
    $chunk

    A:
"""
)

prompt_ru = prompt_ru_template.template
prompt_en = prompt_en_template.template
prompt_ua = prompt_ua_template.template