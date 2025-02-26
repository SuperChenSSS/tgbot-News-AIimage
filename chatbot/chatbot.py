#import configparser
import os
import logging
import redis
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from ChatGPT_HKBU import HKBU_ChatGPT

global redis1
def main():
    #config = configparser.ConfigParser()
    #config.read('config.ini')
    updater = Updater(token=(os.environ["ACCESS_TOKEN_TG"]), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=os.environ['HOST'], 
                         password=os.environ['PASSWORD'],
                         port=os.environ['REDISPORT'],
                         decode_responses=(os.environ['DECODE_RESPONSES']),
                         username=os.environ['USER_NAME']) 
                         
    # Logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # Register dispatcher to handle message
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    # dispatcher for chatgpt
    global chatgpt
    #chatgpt = HKBU_ChatGPT(config)
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatbot)
    dispatcher.add_handler(chatgpt_handler)

    # Add two different commands
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("delete", delete))
    dispatcher.add_handler(CommandHandler("get", get))

    # Start bot
    updater.start_polling()
    updater.idle()

def equiped_chatbot(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    try:
        logging.info("Greeting action on: " + context.args[0])
        msg = context.args[0]
        update.message.reply_text('Good day, ' + msg + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info("Add action on: " + context.args[0])
        msg = context.args[0] # /add keyword
        redis1.incr(msg)
        value = redis1.get(msg)
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        update.message.reply_text("You have said " + msg + " for " + value + " times.")

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def delete(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /delete is issued."""
    try:
        logging.info("Delete action on: " + context.args[0])
        msg = context.args[0] # /delete keyword
        redis1.delete(msg)
        update.message.reply_text("You have deleted " + msg)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete <keyword>')

def get(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /get is issued."""
    try:
        logging.info("Get action on: " + context.args[0])
        msg = context.args[0] # /get keyword
        value = redis1.get(msg)
        if value is None:
            update.message.reply_text("No record for: " + msg)
        else:
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            update.message.reply_text("You have said " + msg + " for " + value + " times.")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /get <keyword>')

if __name__ == '__main__':
    main()