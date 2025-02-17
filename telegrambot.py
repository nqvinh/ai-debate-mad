import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from interactive import Debate

# Telegram Bot Token


class TelegramMadBot:
    def __init__(self, token: str, openai_api_key: str):
        self.token = token
        self.openai_api_key = openai_api_key
        self.MAD_path = os.path.dirname(os.path.abspath(__file__))
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("debate", self.debate))
    
    async def start(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Gửi /debate [chủ đề] để bắt đầu tranh luận!")
    
    async def debate(self, update: Update, context: CallbackContext) -> None:
        if not context.args:
            await update.message.reply_text("Vui lòng nhập chủ đề tranh luận. Ví dụ: /debate AI có thể thay thế con người không?")
            return
        
        debate_topic = " ".join(context.args)
        await update.message.reply_text(f"Bắt đầu tranh luận về: {debate_topic}")
        
        # Load config
        config_path = os.path.join(self.MAD_path, "code/utils/config4all.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        config['debate_topic'] = debate_topic

        chat_id = update.message.chat_id  # Lấy chat_id từ update
        debate = Debate(num_players=3, openai_api_key=self.openai_api_key, config=config, temperature=0, sleep_time=0)
        debate.bot = self  # Assigning the bot instance to the debate object
        debate.update_message = lambda text: self.send_message(chat_id, text)  # Gửi tin nhắn trong debate

        await debate.run()
        
        # Get results
        result = f"===== Kết quả tranh luận =====\n\n"
        result += f"🏷 Chủ đề: {debate.config['debate_topic']}\n\n"
        result += f"✅ Kết luận: {debate.config['debate_answer']}\n\n"
        result += f"📌 Lý do: {debate.config['Reason']}"
        
        await update.message.reply_text(result)
    
    async def send_message(self, chat_id: int, text: str):
        await self.app.bot.send_message(chat_id=chat_id, text=text)


    def run(self):
        self.app.run_polling()

if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = ""
    openai_api_key = ""
    print('init bot!')
    bot = TelegramMadBot(TELEGRAM_BOT_TOKEN, openai_api_key)
    bot.run()
