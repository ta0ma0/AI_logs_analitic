# Logomancy (AI-powered Log Analysis)
Tool for AI sustemd logs analitic

## Описание

Программа для анализа логов systemd (Linux). Собирает логи с помощью journalctl и аналилизирует с помощью AI (Gemini, llama.cpp)

## Установка

### Предварительные требования

Linux (systemd)
Python >= 3.10
llama.cpp - Для работы в автомномном режиме

### Шаги установки

1. Клонируйте репозиторий:

```bash
git clone https://github.com/ta0ma0/Logomancy.git
cd Logomancy
```

2. Установите зависимости

```bash
pip install -r requirements.txt
```
3. Настройте .env

Обязательные поля для уведомления в Telegram.
```
BOT_TOKEN = xxxxxxxxxxxxxxxxxxxxxxxxxxx # Токен бота, взять у Botfather (предварительно надо создать)
CHAT_ID = xxxxxxx # Идентификатор вашего чата (предварительно надо создать), можно увидеть в Web интерфейсе телеграмма в адресной строке.
```

## Использование

1. Перед использованием произвести тестовый запуск. SUDO используется для плучения доступа к файлом логов с помощю journalctl. В дальнейшем работа программы производится из под обычного пользователя.


Из директории с программой.
```
sudo ./run.sh
```

2. Если программа завершилась без ошибок, вы видите отчет data/ai_summary.md. Добавьте cron задание для root

```
sudo crontab -e

Например:

00 10 * * * path_to_programm/run.sh
```