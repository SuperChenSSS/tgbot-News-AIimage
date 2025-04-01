from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
                CallbackContext)
import configparser
import logging
import redis
global redis1
from biying import fetch_and_decode #这里是获得版块分类名，可存sql可不存sql
from sql import delete_database,insert_data,get_data  #这里是对sql操作的函数，用于添加，删除原数据，获得数据的
from get_news import hotpoint,everything #这里是获得新闻的两种方式，hotpoint只能获得当下热点，everything可以进行关键词筛选
from deepseek import DS  #全扔DS


from access_GPT import HKBU_ChatGPT


def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1 
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), 
                password=(config['REDIS']['PASSWORD']), 
                port=(config['REDIS']['REDISPORT']),
                decode_responses=(config['REDIS']['DECODE_RESPONSE']),
                username=(config['REDIS']['USER_NAME']))
   
    # You can set this logging module, so you will know when 
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)
    

    # # register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)
    
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", Hello))
    dispatcher.add_handler(CommandHandler("HP", HP))#有用的
    dispatcher.add_handler(CommandHandler("every", every))#有用的
    dispatcher.add_handler(CommandHandler("DS", DS_filter))#有用的

    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), 
                        equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)#这个是学校的AI
    
    # To start the bot:
    updater.start_polling()
    updater.idle()
def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
 # Define a few command handlers. These usually take the two arguments update and
 # context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def Hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Good day,'+ context.args[0])


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        
        update.message.reply_text('You have said ' + msg +  ' for ' + 
                        redis1.get(msg) + ' times.')
    
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')



def DS_filter(update: Update, context: CallbackContext) -> None:
    msg = DS(hotpoint(),fetch_and_decode())
    update.message.reply_text(msg)

# DS(hotpoint(),fetch_and_decode())


def HP(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(hotpoint())

def every(update: Update, context: CallbackContext) -> None:
    

    logging.info(context.args[0])

    msg = context.args[0]   # /add keyword <-- this should store the keyword
    if context.args[0] != '':
        msg = everything(context.args[0])
        update.message.reply_text(msg)
        
    
    else:
        update.message.reply_text('You have to submita key word to get limited message.')





def equiped_chatgpt(update, context): 
    
    
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))


    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    



if __name__ == '__main__':
    main()

