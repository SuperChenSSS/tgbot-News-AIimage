import os, logging, datetime, threading, s3fs, mysql_db
from telegram import Update, ParseMode, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from ChatGPT_HKBU import HKBU_ChatGPT
from flask import Flask, Response
from dotenv import load_dotenv
from news import latest_news
from zoneinfo import ZoneInfo


#load_dotenv(".terraform/secrets.txt")
# global redis1
global mysql_con
TELEGRAM_MAX_MESSAGE_LENGTH = int(os.environ.get("MAX_TOKEN"))

app = Flask(__name__)  # Flask app instance

@app.route("/health_cmy")
def health_check():
    """Health check endpoint."""
    return Response("OK", status=200)

def main():
    updater = Updater(token=(os.environ["ACCESS_TOKEN_TG"]), use_context=True)
    dispatcher = updater.dispatcher
    global mysql_con
    mysql_con = mysql_db.connect_sql()
                         
    # Logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatbot)
    dispatcher.add_handler(chatgpt_handler)
    
    # Add different commands
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("model", set_model))
    dispatcher.add_handler(CommandHandler("img_summary", img_summary))
    dispatcher.add_handler(CommandHandler("latest_news", get_latest_news))
    dispatcher.add_handler(CommandHandler("news_summary", news_summary))

    # Run the Flask app in a separate thread
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 80, 'debug':False, 'use_reloader': False})
    flask_thread.daemon = True  # Daemonize thread
    flask_thread.start()

    # Set the bot menu
    set_bot_commands(updater.bot)
    # Start bot
    updater.start_polling()
    updater.idle()

def news_summary(update: Update, context: CallbackContext):
    response = "Use AI to summarize...\n" + mysql_db.news_db(mysql_con, "news", 10)
    update.message.reply_text(response)

def get_latest_news(update: Update, context: CallbackContext):
    results = latest_news(mysql_con, 15)
    current_time = datetime.datetime.now(ZoneInfo("Asia/Hong_Kong")).strftime("%Y-%m-%d %H:%M")
    message = "News updated to " + current_time + "\n"
    for (title, link) in results.items():
        message += f'<a href="{link}">{title}</a>\n'
    message += "News written to DB completed.\n"
    update.message.reply_text(message, parse_mode=ParseMode.HTML)

def img_summary(update: Update, context: CallbackContext):
    global chatgpt
    chatgpt.current_model = "gemini"
    response = mysql_db.gpt_summary(mysql_con, "ai_image", 5, chatgpt.current_model)
    update.message.reply_text(response)

def set_bot_commands(bot):
    """Sets the bot's menu commands."""
    bot_commands = [
        BotCommand("/latest_news", "Get the latest news"),
        BotCommand("/news_summary", "Get the AI summary of the latest news"),
        BotCommand("/img_summary", "Give a summary of AI generated images"),
        BotCommand("/model", "Select the model to use (chatgpt/gemini)"),
    ]
    bot.set_my_commands(bot_commands)

def set_model(update: Update, context: CallbackContext) -> None:
    """Set the model to be used by the chatbot."""
    global chatgpt
    try:
        model = context.args[0].lower()
        if model in ["chatgpt", "gemini"]:
            chatgpt.current_model = model
            update.message.reply_text(f"Model set to {model}.")
        else:
            update.message.reply_text("Invalid model. Choose 'chatgpt' or 'gemini'.")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /model <chatgpt/gemini>')

def split_message(text, max_length=TELEGRAM_MAX_MESSAGE_LENGTH):
    """Splits a long message into multiple messages of a maximum length."""
    if len(text) <= max_length:
        return [text]
    else:
        parts = []
        while len(text) > max_length:
            split_point = text.rfind(' ', 0, max_length)  # Find a space to split at
            if split_point == -1:
                split_point = max_length # if no space, just split at max length
            parts.append(text[:split_point])
            text = text[split_point:]
        parts.append(text)
        return parts
    
def equiped_chatbot(update, context):
    global chatgpt, mysql_con
    if not hasattr(chatgpt, 'current_model'):
        chatgpt.current_model = "gemini"
        logging.warning("chatgpt.current_model was not set. Defaulting to 'gemini'.")
    message_text = update.message.text
    img_keywords = os.environ.get("IMG_WORDS").replace("\"","").split(",")
    # logging.info("Image Keywords: " + str(img_keywords))
    if any(keyword in message_text.lower() for keyword in img_keywords):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Image Generation in Progress, this could take about 30 seconds...")
        try:
            s3_path = chatgpt.submit(message_text, "image")
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")
        if s3_path:
            s3 = s3fs.S3FileSystem(anon=False)
            with s3.open(s3_path, 'rb') as f:
                photo_data = f.read()
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_data, timeout=70, caption="Prompt: " + message_text)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Image Generation Completed, now send to DB...")
            timestamp = datetime.datetime.now(ZoneInfo("Asia/Hong_Kong")).strftime("%Y-%m-%d %H:%M:%S")
            mysql_db.insert_db("ai_image", mysql_con, timestamp, message_text, s3_path)
            context.bot.send_message(chat_id=update.effective_chat.id, text="DB Stored Successfully.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I can't generate an image for that.")
    else:
        reply_message = chatgpt.submit(message_text, chatgpt.current_model)
        logging.info("Update: " + str(update))
        logging.info("Context: " + str(context))
        # Split the message if it's too long
        message_parts = split_message(reply_message)
        for part in message_parts:
            context.bot.send_message(chat_id=update.effective_chat.id, text=part)

def echo(update, context):
    """Echo the user message in lowercase.
    
    :param update: Make update.message.text to upper case
    :type update: str
    :param context: Reply with context
    :type context: str
    :return: lowercase of the message
    :rtype: str
    """
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def hello(update: Update, context: CallbackContext) -> None:
    """Greetings with hello with /hello "keyword".

    :param update: not using the input for this function
    :type update: str
    :param context: Reply with Good day, "keyword"!
    :type context: str
    """
    try:
        msg = context.args[0]
        logging.info("Greeting action on: " + msg)
        update.message.reply_text('Good day, ' + msg + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

if __name__ == '__main__':
    main()