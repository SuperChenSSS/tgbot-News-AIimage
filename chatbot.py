#import configparser
import os
import logging
import redis
from telegram import Update, ParseMode, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from ChatGPT_HKBU import HKBU_ChatGPT
import re

global redis1
TELEGRAM_MAX_MESSAGE_LENGTH = int(os.environ.get("MAX_TOKEN"))

def main():
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
    dispatcher.add_handler(CommandHandler("model", set_model))

    # Set the bot menu
    set_bot_commands(updater.bot)
    # Start bot
    updater.start_polling()
    updater.idle()

def set_bot_commands(bot):
    """Sets the bot's menu commands."""
    bot_commands = [
        BotCommand("/help", "Show help message"),
        BotCommand("/add", "Add a keyword to the database"),
        BotCommand("/delete", "Delete a keyword from the database"),
        BotCommand("/get", "Get the count of a keyword"),
        BotCommand("/set", "Change a keyword to another"),
        BotCommand("/hello", "Greet the user"),
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
    
def escape_markdown_v2(text):
    """Escapes reserved characters for Telegram's MarkdownV2."""
    escape_chars = r"_\*\[\]\(\)~`>#\+\-=|\.!{}"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def equiped_chatbot(update, context):
    global chatgpt
    if not hasattr(chatgpt, 'current_model'):
        chatgpt.current_model = "gemini"
        logging.warning("chatgpt.current_model was not set. Defaulting to 'gemini'.")
    reply_message = chatgpt.submit(update.message.text, chatgpt.current_model)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    # Split the message if it's too long
    message_parts = split_message(reply_message)
    for part in message_parts:
        escaped_part = escape_markdown_v2(part)
        context.bot.send_message(chat_id=update.effective_chat.id, text=escaped_part, parse_mode=ParseMode.MARKDOWN_V2)
    # context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

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

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """A placeholder when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

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

def add(update: Update, context: CallbackContext) -> None:
    """Add a message to DB when the command /add is issued.

    :param update: args[0] as the keyword
    :type update: str
    :param context: Reply with You have said args[0] for "value" times.
    :type context: str
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

    :param update: args[0] as the keyword
    :type update: str
    :param context: Reply with You have deleted "keyword".
    :type context: str
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

    :param update: args[0] as the keyword to be changed, args[1] as the new keyword
    :type update: str
    :param context: Reply with args[0] changed to args[1]
    :type context: str
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

    :param update: args[0] as the keyword
    :type update: str
    :param context: Reply with Number of occurence of the keyword.
    :type context: str
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