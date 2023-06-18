from fast_bitrix24  import Bitrix
from dotenv import load_dotenv
import os
from pprint import pprint
load_dotenv()
webHook = ''
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

def create_contact():
    pass

deal_history()
