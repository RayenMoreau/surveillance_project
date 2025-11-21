from telegram import Bot
import asyncio

TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updates = await bot.get_updates()
    
    if not updates:
        print("Send a message to your bot first, then run again")
    else:
        for update in updates:
            if update.message:
                chat_id = update.message.chat.id
                chat_title = update.message.chat.title or "Private Chat"
                print(f"Chat ID: {chat_id} | Title: {chat_title}")

asyncio.run(main())
