import os
import asyncio # Добавляем asyncio
import telegram
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

async def send(text):
    bot = telegram.Bot(token=BOT_TOKEN)
    # await bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=reply_markup)
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def main():
    # Пример использования функции send_with_button
    await send("Нажмите на кнопку ниже, чтобы открыть ссылку:", "http://example.com")

if __name__ == '__main__':
    asyncio.run(main())