from fast_bitrix24  import Bitrix
from dotenv import load_dotenv
import os
from pprint import pprint
from loguru import logger
load_dotenv()
webHook = os.environ.get('webHook')
bit = Bitrix(webHook)

def deal_history():

    row = { 
        'entityTypeId': 2,
        'order': { "ID": "ASC" },
        'filter': { "OWNER_ID": 4089 },
        'select': [ "ID", "STAGE_ID", "CREATED_TIME",'STAGE_SEMANTIC_ID' ],
        'start': 2,
    }
    dealHist = bit.call("crm.stagehistory.list", row)
    pprint(dealHist)

def create_lead(items:dict):
    dealID = bit.call('crm.lead.add', items=items,raw=True)
    return dealID

def update_deal(phone:str, text:str, nicname:str = 'Клиент из Telegram'):
    phone = phone.replace('8','+7',1)
    leads = bit.get_all(
    'crm.lead.list',
    params={
        #'select': ['*', 'UF_*'],
        'filter': {'PHONE': phone}
    })
    logger.info(f'{len(leads)=}')
    if len(leads) >= 1:
        params = {"ID": leads[0]['ID'], "fields": {"UF_CRM_1689546544": text}}
        bit.call('crm.lead.update', params, raw=True)
    else:
        params = {"NAME": nicname, 
                  "fields": {"UF_CRM_1689546544": text,
                             "PHONE":[{ "VALUE": phone, "VALUE_TYPE": "WORK" }]}}
        create_lead(params)
# добавить комментарий к задаче
    print(f'{leads=}')
    pass

def create_contact():
    pass
#phone = '+79308316655'
#params = {"NAME": 'nicname', 
#                  "fields": {"UF_CRM_1689546544": 'text',
#                             "PHONE":[{'VALUE': phone, 'VALUE_TYPE': 'WORK'}]}}
                  
#create_lead(params)
#deal_history()
