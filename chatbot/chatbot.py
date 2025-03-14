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
    dispatcher.add_handler(CommandHandler("set", set))

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
    """Echo the user message in lowercase.
    
    :param: args[0] as message
    :return: lowercase of the message
    :rtype: send_message
    """
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """A placeholder when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello(update: Update, context: CallbackContext) -> None:
    """Greetings with hello with /hello <keyword>.

    :param: None
    :return context: Good day, <keyword>!
    """
    try:
        msg = context.args[0]
        logging.info("Greeting action on: " + msg)
        update.message.reply_text('Good day, ' + msg + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

def add(update: Update, context: CallbackContext) -> None:
    """Add a message to DB when the command /add is issued.

    :param: args[0] as the keyword
    :return: You have said args[0] for <value> times.
    :rtype: reply_text
    """
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
    """Delete a message when the command /delete is issued.

    :param: args[0] as the keyword
    :return: You have deleted <keyword>.
    :rtype: reply_text
    """
    try:
        logging.info("Delete action on: " + context.args[0])
        msg = context.args[0] # /delete keyword
        redis1.delete(msg)
        update.message.reply_text("You have deleted " + msg)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete <keyword>')

def set(update: Update, context: CallbackContext) -> None:
    """Set args[0] to args[1] when the command /set is issued.

    :param: args[0] as the keyword to be changed, args[1] as the new keyword
    :return: args[0] changed to args[1]
    :rtype: reply_text
    """
    try:
        logging.info("Set action on: " + context.args[0] + " to " + context.args[1])
        keywordA = context.args[0] # /set keywordA keywordB
        keywordB = context.args[1]
        value = redis1.get(keywordA)
        if value is None:
            update.message.reply_text("No record for: " + keywordA)
        else:
            redis1.set(keywordB, value)
            redis1.delete(keywordA)
            update.message.reply_text(keywordA + " changed to " + keywordB)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <keywordA> <keywordB>')



def get(update: Update, context: CallbackContext) -> None:
    """Get the number of occurence with keyword: args[0] when the command /get is issued.

    :param: args[0] as the keyword
    :return: Number of occurence of the keyword.
    :rtype: reply_text
    """
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