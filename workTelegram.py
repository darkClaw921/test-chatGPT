import os
import random
import telebot
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
from datetime import datetime
import workYDB
load_dotenv()

gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
# инициализация бота и диспетчера
#dp = Dispatcher(bot)
sql = workYDB.Ydb()
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/edit?usp=sharing')
#answer = gpt.answer(expert_promt, 
#           'Я хочу, чтобы после завершения обучения мне подобрали работу')
#print(answer)
models = {
    'model1': 'https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/edit?usp=sharing',
    'model2': 'https://docs.google.com/document/d/1deHxH4rTpuJLJ0fnvsWJe8RwFbpju0-hVLLqklnlAL4/edit?usp=sharing'
}

def time_epoch():
    from time import mktime
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return int(millis_since_epoch)

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    row = {'id': message.chat.id, 'payload': '',}
    sql.replace_query('user', row)

    bot.send_message(message.chat.id,'/model1 - модель 1 Просто обычный чат после /context пришлет отчет по клиенту\n', 
                     parse_mode='markdown')

@bot.message_handler(commands=['context'])
def send_button(message):
    payload = sql.get_payload(message.chat.id)
    context = sql.get_context(message.chat.id, payload)
    model = models[payload]
    if payload == 'model1':
        print('это model2')
        model = models['model2']        
    validation_promt = gpt.load_prompt(model)

    answer = gpt.answer(validation_promt, context, temp = 0.1)
    sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
    sql.set_payload(message.chat.id, ' ')
    bot.send_message(message.chat.id, answer)
    bot.send_message(message.chat.id, 
        "Контекст сброшен",)

@bot.message_handler(commands=['model1'])
def dialog_model1(message):
    #payload = sql.get_payload(message.chat.id)
    sql.set_payload(message.chat.id, 'model1')
    bot.send_message(message.chat.id,'Что вы хотите узнать?',)


@bot.message_handler(content_types=['text'])
def any_message(message):
    print('это сообщение', message)
    text = message.text.lower()
    userID= message.chat.id
    payload = sql.get_payload(userID)
    
    context = sql.get_context(userID, payload)
    if context is None or context == '' or context == []:
        context = text

    print('context2', context + f'клиент: {text}')
    model= gpt.load_prompt(models[payload])
    answer = gpt.answer(model, text, temp = 0.1)
    print('answer', answer)
    bot.send_message(message.chat.id, answer)
    #if payload == 'model3':
    rows = {'id': time_epoch(),'MODEL_DIALOG': payload, 'TEXT': f'клиент: {text}'}
    sql.insert_query(userID,  rows)

    rows = {'id': time_epoch()+1,'MODEL_DIALOG': payload, 'TEXT': f'менеджер: {answer}'}
    sql.insert_query(userID,  rows)

bot.infinity_polling()