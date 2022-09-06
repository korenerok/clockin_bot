from configparser import ConfigParser
import logging
import clockin_stats as stats
from telegram.ext import Updater, MessageHandler, Filters,CommandHandler

config = ConfigParser().read("./.env")
settings = config['SETTINGS_BOT']
chatIdResponse=settings['RESPONSE_TO_CHAT_ID']
token = settings['TELEGRAM_TOKEN']

def start(update, context):
    update.message.reply_text("Clockin bot started")

def process_messages(update,context):
    text = update.message.text
    telegram_id = str(update.message.from_user.id)
    user = update.message.from_user.username
    fullName = f"""{update.message.from_user.first_name} {update.message.from_user.last_name if update.message.from_user.last_name else ""} """
#    print(f""" {telegram_id} {fullName} {user} {text}""")
#    print(update)
    response=None
    #standarize and strip text message
    text=text.strip().lower()
    if text== 'in':
        response = stats.addDataIn(telegram_id, fullName, user)
    elif text== 'out':
        response = stats.addDataOut(telegram_id, fullName, user)
    if response is not None:
        context.bot.send_message(
            chat_id = chatIdResponse,
            text = response,
            parse_mode="Markdown"
            )
    

def dayHours(update, context):
    response =str(stats.calculateDayHours())
    update.message.reply_text(response)

def weekHours(update, context):
    response =str(stats.calculateWeekHours())
    update.message.reply_text(response)
        

if __name__ == '__main__':
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('dayhours', dayHours))
    dispatcher.add_handler(CommandHandler('weekhours', weekHours))
    dispatcher.add_handler(MessageHandler(filters=Filters.text, callback= process_messages))
    dispatcher.add_handler(MessageHandler(filters=Filters.caption, callback= process_messages))
    updater.start_polling()
    
    print('Bot started')
    updater.idle()



