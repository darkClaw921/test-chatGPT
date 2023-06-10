import os
import random
import telebot
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
from datetime import datetime
import workYDB
import redis
import json
from loguru import logger
import sys
load_dotenv()

logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("file_1.log", rotation="50 MB")
gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
# инициализация бота и диспетчера
#dp = Dispatcher(bot)
sql = workYDB.Ydb()
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/edit?usp=sharing')
#answer = gpt.answer(expert_promt, 
#           'Я хочу, чтобы после завершения обучения мне подобрали работу')
r = redis.Redis(host='localhost', port=6379, decode_responses=False)
#print(answer)
model_index=gpt.load_search_indexes('https://docs.google.com/document/d/1nMjBCoI3WpWofpVRI0rsi-iHjVSeC358JDwN96UWBrM/edit?usp=sharing')
url = 'https://docs.google.com/document/d/1f4GMt2utNHsrSjqwE9tZ7R632_ceSdgK6k-_QwyioZA/edit?usp=sharing'
model= gpt.load_prompt(url)
#models2 = {
#    'model1': 'https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/edit?usp=sharing',
#    'model2': 'https://docs.google.com/document/d/1deHxH4rTpuJLJ0fnvsWJe8RwFbpju0-hVLLqklnlAL4/edit?usp=sharing'
#}

def time_epoch():
    from time import mktime
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return int(millis_since_epoch)

def get_model_url(modelName: str):
    modelUrl = sql.select_query('model', f'model = "{modelName}"')[0]['url']
    logger.info(f'get_model_url {modelUrl}')
    #print('a', modelUrl)
    return modelUrl.decode('utf-8')

def add_message_to_history(userID:str, role:str, message:str):
    mess = {'role': role, 'content': message}
    r.lpush(userID, json.dumps(mess))

def get_history(userID:str):
    items = r.lrange(userID, 0, -1)
    history = [json.loads(m.decode("utf-8")) for m in items[::-1]]
    return history

def add_old_history(userID:str, history:list):
    his = history.copy()
    clear_history(userID)
    for i in his:
        mess = i
        r.lpush(userID, json.dumps(mess))


def clear_history(userID:str):
    r.delete(userID)

@bot.message_handler(commands=['addmodel'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addmodel')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку promt google document и через пробел название модели (model1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)
    

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    row = {'id': message.chat.id, 'payload': '',}
    sql.replace_query('user', row)
    

    bot.send_message(message.chat.id,'/addmodel добавление новой модели\n/model1 - модель 1 Просто обычный чат /context сбросит контекст по текущей модели\nДоюавление моделей кроме model1 пока нельзя\n/restart перезапись главного документа', 
                     parse_mode='markdown')
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/')

@bot.message_handler(commands=['restart'])
def restart_modal_index(message):
    global model_index 
    model_index=gpt.load_search_indexes('https://docs.google.com/document/d/1nMjBCoI3WpWofpVRI0rsi-iHjVSeC358JDwN96UWBrM/edit?usp=sharing')

@bot.message_handler(commands=['context'])
def send_button(message):
    payload = sql.get_payload(message.chat.id)
    

    #answer = gpt.answer(validation_promt, context, temp = 0.1)
    sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
    sql.set_payload(message.chat.id, ' ')
    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id, 
        "Контекст сброшен",)

@bot.message_handler(commands=['model1'])
def dialog_model1(message):
    #payload = sql.get_payload(message.chat.id)
    sql.set_payload(message.chat.id, 'model1')
    bot.send_message(message.chat.id,'Что вы хотите узнать?',)


@bot.message_handler(content_types=['text'])
def any_message(message):
    #print('это сообщение', message)
    #text = message.text.lower()
    text = message.text
    userID= message.chat.id
    payload = sql.get_payload(userID)
    
    if payload == 'addmodel':
        text = text.split(' ')
        rows = {'model': text[1], 'url': text[0] }
        #sql.insert_query('model',rows)
        sql.replace_query('model',rows)
        return 0
    #context = sql.get_context(userID, payload)
    #if context is None or context == '' or context == []:
        #context = text
    add_message_to_history(userID, 'user', text)
    history = get_history(str(userID))


    #print('context2', context + f'клиент: {text}')
    #model= gpt.load_prompt('https://docs.google.com/document/d/1f4GMt2utNHsrSjqwE9tZ7R632_ceSdgK6k-_QwyioZA/edit?usp=sharing')
    #model= gpt.load_prompt(get_model_url(payload))
    #model= gpt.load_prompt(get_model_url(payload))
    #answer = gpt.answer(model, text, temp = 0.1)
    #answer = gpt.answer_index(model, text, model_index,)
    
    try:
        answer = gpt.answer_index(model, text, history, model_index, verbose=0)
        logger.info(f'ответ сети если нет ощибок: {answer}')
        #print('мы получили ответ \n', answer)
    except Exception as e:
        bot.send_message(userID, e)
        bot.send_message(userID, 'начинаю sammury: ответ может занять больше времени, но не более 3х минут')
        history = get_history(str(userID))
        summaryHistory = gpt.get_summary(history)
        logger.info(f'summary истории {summaryHistory}')
        #print(f'summary: {summaryHistory}')
        logger.info(f'история до summary {history}')
        #print('история до очистки \n', history)
        #print('история summary \n', summaryHistory)
        #clear_history(userID)
        history = [summaryHistory]
        history.extend([{'role':'user', 'content': text}])
        add_old_history(userID,history)
        history = get_history(str(userID))
        logger.info(f'история после summary {history}')
        #print('история после очистки\n', history)
        
        answer = gpt.answer_index(model, text, history, model_index, verbose=0)
        bot.send_message(message.chat.id, answer)
        add_message_to_history(userID, 'assistant', answer)

        return 0 
    #answer, answerBlock = gpt.answer_index(model, context, model_index, verbose=1)
    #print('answer_index', answer)
    add_message_to_history(userID, 'assistant', answer)
    #b = gpt.get_summary(history)
    #print(f'{b=}')
    #for i in answerBlock:
    #    bot.send_message(message.chat.id, i)
    
    bot.send_message(message.chat.id, answer)
    #if payload == 'model3':
    rows = {'id': time_epoch(),'MODEL_DIALOG': payload, 'TEXT': f'клиент: {text}'}
    sql.insert_query(userID,  rows)

    rows = {'id': time_epoch()+1,'MODEL_DIALOG': payload, 'TEXT': f'менеджер: {answer}'}
    sql.insert_query(userID,  rows)

bot.infinity_polling()
