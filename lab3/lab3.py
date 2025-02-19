import configparser
import logging
import redis
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

global redis1
def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=config['REDIS']['HOST'], 
                         password=config['REDIS']['PASSWORD'],
                         port=config['REDIS']['REDISPORT'],
                         decode_responses=(config['REDIS']['DECODE_RESPONSES']),
                         username=config['REDIS']['USER_NAME']) 
                         
    # Logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # Register dispatcher to handle message
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # Add two different commands
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("delete", delete))

    # Start bot
    updater.start_polling()
    updater.idle()

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

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
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
        logging.info(context.args[0])
        msg = context.args[0] # /delete keyword
        redis1.delete(msg)
        update.message.reply_text("You have deleted " + msg)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete <keyword>')

if __name__ == '__main__':
    main()