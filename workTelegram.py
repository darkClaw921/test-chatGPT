import os
import random
import telebot
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
from datetime import datetime
import workYDB
import redis
import json
from loguru import logger
import sys
from createKeyboard import create_menu_keyboard
from workBitrix import *
from helper import *
from workGDrive import *
from telebot.types import InputMediaPhoto
from workRedis import *
import workGS
from workFaiss import *
load_dotenv()


logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("file_1.log", rotation="50 MB")
gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
sheet = workGS.Sheet('kgtaprojects-8706cc47a185.json','цены на дома 4.0 актуально ')
# инициализация бота и диспетчера
#dp = Dispatcher(bot)
sql = workYDB.Ydb()
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/edit?usp=sharing')
#answer = gpt.answer(expert_promt, 
#           'Я хочу, чтобы после завершения обучения мне подобрали работу')
URL_USERS = {}
#r = redis.Redis(host='localhost', port=6379, decode_responses=False)
#print(answer)
MODEL_URL= 'https://docs.google.com/document/d/1nMjBCoI3WpWofpVRI0rsi-iHjVSeC358JDwN96UWBrM/edit?usp=sharing'
gsText = sheet.get_gs_text()
model_index=gpt.load_search_indexes(MODEL_URL, gsText=gsText)
model_project = gpt.create_embedding(gsText)
PROMT_URL = 'https://docs.google.com/document/d/1f4GMt2utNHsrSjqwE9tZ7R632_ceSdgK6k-_QwyioZA/edit?usp=sharing'
model= gpt.load_prompt(PROMT_URL)
PROMT_URL_SUMMARY ='https://docs.google.com/document/d/1XhSDXvzNKA9JpF3QusXtgMnpFKY8vVpT9e3ZkivPePE/edit?usp=sharing'
PROMT_PODBOR_HOUSE = 'https://docs.google.com/document/d/1WTS8SQ2hQSVf8q3trXoQwHuZy5Q-U0fxAof5LYmjYYc/edit?usp=sharing'

info_db=create_info_vector()

@bot.message_handler(commands=['addmodel'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addmodel')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку promt google document и через пробел название модели (model1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)
    

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    username = message.from_user.username
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    #row = {'id': message.chat.id, 'payload': '',}
    row = {'id': message.chat.id, 'model': '', 'promt': '','nicname':username, 'payload': ''}
    sql.replace_query('user', row)
    
    text = """Здравствуйте, я AI ассистент компании Сканди ЭкоДом. Я отвечу на Ваши вопросы по поводу строительства загородного дома и задам свои 😁. Хотите я Вам расскажу про варианты комплектации домов?
    """
    bot.send_message(message.chat.id, text, 
                     parse_mode='markdown',
                     reply_markup= create_menu_keyboard())
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/')

@bot.message_handler(commands=['restart'])
def restart_modal_index(message):
    global model_index, model 
    model_index=gpt.load_search_indexes(MODEL_URL)
    #url = 'https://docs.google.com/document/d/1f4GMt2utNHsrSjqwE9tZ7R632_ceSdgK6k-_QwyioZA/edit?usp=sharing'
    #model= gpt.load_prompt(url)
    model= gpt.load_prompt(PROMT_URL)
    bot.send_message(message.chat.id, 'Обновлено', 
                     parse_mode='markdown',
                     reply_markup= create_menu_keyboard())

@bot.message_handler(commands=['context'])
def send_button(message):
    payload = sql.get_payload(message.chat.id)
    

    #answer = gpt.answer(validation_promt, context, temp = 0.1)
    sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
    sql.set_payload(message.chat.id, ' ')
    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id, 
        "Контекст сброшен",reply_markup=create_menu_keyboard(),)

@bot.message_handler(commands=['model1'])
def dialog_model1(message):
    #payload = sql.get_payload(message.chat.id)
    sql.set_payload(message.chat.id, 'model1')
    bot.send_message(message.chat.id,'Что вы хотите узнать?',)

#@logger.catch
@bot.message_handler(content_types=['text'])
def any_message(message):
    global URL_USERS
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
    logger.info(f'история {history}')


    try:
        logger.info(f'{PROMT_URL}')
        model= gpt.load_prompt(PROMT_URL) 
    except:
        model= gpt.load_prompt(PROMT_URL) 

    lastMessage = history[-1]['content'] 
        
    try:
        if text == 'aabb':
            1/0
        answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, lastMessage+text, history, model_index,temp=0.5, verbose=0)
        
        if len(history) < 3: 
            answerInfo = {'type': 'no'} 
            logger.warning(f'{answerInfo=}')
        else: 
            answerInfo = answer_info(lastMessage+text, info_db)
            logger.warning(f'{answerInfo=}')
        if answerInfo['type'] == 'podborka':
            
            bot.send_message(userID, 'подбираю проекты')
            promtPodbor = gpt.load_prompt(PROMT_PODBOR_HOUSE)
            logger.warning(f'{promtPodbor=}')
            hist =  get_history(str(userID))
            logger.info(f'{hist=}')
            summary= gpt.summarize_podborka(promtPodbor, history=hist)
            #history = [history]
            #history.extend([{'role':'user', 'content': text}])
            #add_old_history(userID,history)
            history = get_history(str(userID))
        
            logger.warning(f'{summary=}')
            logger.warning(f'{history=}')
            promtSmmary = f'Отправь клиенту подборку наиболее подходящих проектов по этим критериям: {summary}'
            #answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, lastMessage+text, history, model_index,temp=0.5, verbose=0)
            logger.warning(f'{promtSmmary=}')
            history=[]
            answer, allToken, allTokenPrice, message_content = gpt.answer_index(promtSmmary, summary, history, model_index,temp=0.5, verbose=0)
            bot.send_message(message.chat.id, answer,  parse_mode='markdown') 

            return 0 
        #answerProject = gpt.search_project(model_project, lastMessage+answer,4,1)
        #logger.info(f'{answerProject=}')
        logger.info(f'ответ сети если нет ощибок: {answer}')
        #print('мы получили ответ \n', answer)
    except Exception as e:
        bot.send_message(userID, e)
        #bot.send_message(userID, 'начинаю sammury: ответ может занять больше времени, но не более 3х минут')
        history = get_history(str(userID))
        #summaryHistory = gpt.get_summary(history)
        summaryHistory1 = gpt.summarize_questions(history)
        logger.info(f'summary истории1 {summaryHistory1}')
        #logger.info(f'summary истории {summaryHistory}')
        #print(f'summary: {summaryHistory}')
        #logger.info(f'история до summary {history}')
        #print('история до очистки \n', history)
        #print('история summary \n', summaryHistory)
        #clear_history(userID)
        history = [summaryHistory1]
        history.extend([{'role':'user', 'content': text}])
        add_old_history(userID,history)
        history = get_history(str(userID))
        logger.info(f'история после summary {history}')
        #print('история после очистки\n', history)
        
        #answer = gpt.answer_index(model, text, history, model_index,temp=0.2, verbose=1)
        answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, text, history, model_index,temp=0.5, verbose=0)
        bot.send_message(message.chat.id, answer)
        add_message_to_history(userID, 'assistant', answer)

        return 0 
    
    #if message_content 
    #answer, answerBlock = gpt.answer_index(model, context, model_index, verbose=1)
    #print('answer_index', answer)
    add_message_to_history(userID, 'assistant', answer)
    #b = gpt.get_summary(history)
    #print(f'{b=}')
    #for i in answerBlock:
    #    bot.send_message(message.chat.id, i)
    prepareAnswer= answer.lower()
    #print(f'{prepareAnswer=}')
    #print(f"{prepareAnswer.find('спасибо за предоставленный номер')=}") 
    b = prepareAnswer.find('спасибо за предоставленный номер') 
    print(f'{b=}')

    logger.info(f'{message_content=}')
        
    photoFolder = message_content[0].page_content.find('https://drive') 
    logger.info(f'{photoFolder=}')
    bot.send_message(message.chat.id, answer,  parse_mode='markdown')
    media_group = [] 
    if photoFolder >= 0:
        logger.info(f'{URL_USERS=}')
        #TODO удалить если нужно чтобы фото отправлялись по 1 разу
        URL_USERS={}
        bot.send_message(message.chat.id, 'Подождите, ищу фото проектов...',  parse_mode='markdown')
        for mes_content in message_content:
            mes_content= mes_content.page_content
            #media_group.extend(media_group1)
            try:
                URL_USERS, media_group,nameProject = download_photo(mes_content,URL_USERS,userID)
                if media_group == []:
                    continue
                bot.send_message(message.chat.id, f'Отправляю фото проекта {nameProject}...',  parse_mode='markdown')
                bot.send_media_group(message.chat.id, media_group,)
            except Exception as e:
                bot.send_message(message.chat.id, 'Извините, не могу найти актуальные фото',  parse_mode='markdown') 
                bot.send_message(message.chat.id, e,  parse_mode='markdown')
    if b >= 0:
        print(f"{prepareAnswer.find('cпасибо за предоставленный номер')=}")
        PROMT_SUMMARY = gpt.load_prompt(PROMT_URL_SUMMARY)
        history = get_history(str(userID))
        history_answer = gpt.answer(PROMT_SUMMARY,history)[0]
        print(f'{history_answer=}')
        print(f'{answer=}')
        #bot.send_message(message.chat.id, answer)
        phone = slice_str_phone(history_answer)
        pprint(f"{phone=}")
        
        print('запиь в битрикс')
        update_deal(phone, history_answer)

    #try:
    #    bot.send_media_group(message.chat.id, media_group)
    #except Exception as e:
    #    bot.send_message(message.chat.id, e,  parse_mode='markdown')

    #if payload == 'model3':
    now = datetime.now()+timedelta(hours=3)
    #now = datetime.now()
# Format the date and time according to the desired format
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    #answer, allToken, allTokenPrice= gpt.answer(' ',mess,)
    row = {'all_price': float(allTokenPrice), 'all_token': int(allToken), 'all_messages': 1}
    sql.plus_query_user('user', row, f"id={userID}")
    
    username = message.from_user.username
    rows = {'time_epoch': time_epoch(),
            'MODEL_DIALOG': payload,
            'date': formatted_date,
            'id': userID,
            'nicname': username,
            #'token': username,
            #'token_price': username,
            'TEXT': f'Клиент: {text}'}
    sql.insert_query('all_user_dialog',  rows)
    
    rows = {'time_epoch': time_epoch(),
            'MODEL_DIALOG': payload,
            'date': formatted_date,
            'id': userID,
            'nicname': username,
            'token': allToken,
            'token_price': allTokenPrice,
            'TEXT': f'Менеджер: {answer}'}
    sql.insert_query('all_user_dialog',  rows)


    

bot.infinity_polling()
