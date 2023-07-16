from fast_bitrix24  import Bitrix
from dotenv import load_dotenv
import os
from pprint import pprint
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

def create_deal(items:dict):
    dealID = bit.call('crm.deal.add', items=items)
    return dealID

def update_deal(phone:str, text:str):
    phone = phone.replace('8','+7',1)
    leads = bit.get_all(
    'crm.lead.list',
    params={
        #'select': ['*', 'UF_*'],
        'filter': {'PHONE': phone}
    })
    if len(leads) >= 1:
        params = {"ID": leads[0]['ID'], "fields": {"UF_CRM_1689546544": text}}
        bit.call('crm.lead.update', params, raw=True)

# добавить комментарий к задаче
    print(f'{leads=}')
    pass

def create_contact():
    pass

#deal_history()
