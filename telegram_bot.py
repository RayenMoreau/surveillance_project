import asyncio
from telegram import Bot
from config import Config

class TelegramNotifier:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.bot = None
        self.last_notification_time = {}
        self.cooldown = Config.NOTIFICATION_COOLDOWN
        
        if self.bot_token and self.chat_id:
            self.bot = Bot(token=self.bot_token)
            print("Telegram notifier initialized")
        else:
            print("Warning: Telegram token or chat ID not set")
    
    async def send_message_async(self, message):
        """Send message asynchronously"""
        if not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def send_message(self, message):
        """Send message (synchronous wrapper)"""
        return asyncio.run(self.send_message_async(message))
    
    def send_access_granted(self, name):
        """Send access granted notification"""
        if not self.should_send_notification(f"access_{name}"):
            return False
            
        msg = f"✅ <b>Access Granted</b>\nName: {name}\nTime: {self.get_timestamp()}"
        return self.send_message(msg)
    
    def send_unknown_person(self):
        """Send unknown person alert"""
        if not self.should_send_notification("unknown"):
            return False

        msg = f"🚨 <b>Unknown Person Detected!</b>\nTime: {self.get_timestamp()}"
        return self.send_message(msg)
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def should_send_notification(self, person_name):
        """Check if enough time has passed since last notification"""
        import time
        current_time = time.time()
        last_time = self.last_notification_time.get(person_name, 0)
        
        if current_time - last_time > self.cooldown:
            self.last_notification_time[person_name] = current_time
            return True
        return False
