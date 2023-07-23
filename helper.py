import re
import telebot
from loguru import logger
# any

def remove_empty_lines(text):
    lines = text.splitlines()  # Разделение текста на отдельные строки
    stripped_lines = (line.strip() for line in lines)  # Удаление начальных и конечных пробелов
    non_empty_lines = (line for line in stripped_lines if line)  # Отбор только непустых строк
    return "\n".join(non_empty_lines) 

def slice_str(s:str,start:str, end:str):
    a = s.find(start)
    print(a)
    if a == -1:
        return ' '
    return s[s.find(start)+len(start):s.find(end)]

def slice_str_phone(message:str,):
    
    #return s[s.find(start)+len(start):s.find(start)+len(start)+18]
    #a = """Client's name: \nCustomer's phone number: 79777345754\n\nConfiguration at the customer's choice (closed circuit, warm circuit, exterior finish): \nThe amount that the client expects to pay: \nDoes the client have a home design: No\nArchitectural style that the client likes: Modern\nDoes the client need a house for permanent residence or for a weekend vacation: Permanent residence\nThe number of beds and the size of the client's family: Big family\nThe parameters of the house desired by the client: 3 floors, 2 bedrooms\nWhen the client plans to move:\nDoes the client need a mortgage:\nProjects that the client liked (project names only):"""
#b = slice_str(a, '\n','Configuration')
    logger.info(f'{message=}')
    #b = slice_str(message, 'phone number:','Configuration').strip()
    b = slice_str(message, 'Номер телефона клиента:','Конфигурация').strip()
    logger.info(f'вырезаный телефон ', b)
    return b


def sum_dict_values(dict1, dict2):
    result = {}

    for key in dict1:
        if key in dict2:
            result[key] = dict1[key] + dict2[key]
        else:
            result[key] = dict1[key]

    for key in dict2:
        if key not in dict1:
            result[key] = dict2[key]

    return result

def extract_id_from_url(url):
    id_start_index = url.rfind('/') + 1
    id_end_index = url.find('?') if '?' in url else len(url)
    return url[id_start_index:id_end_index]

def extract_url(text):
    pattern = re.compile(r'(https?://\S+)')
    match = pattern.search(text)
    if match:
        return match.group(1).replace(')','')
    else:
        return None
    
def create_media_gorup(lst:list):
    media_group = telebot.types.MediaGroup()
    for i in lst:
        photo = open(i, 'rb')
        media_group.attach_photo(photo)
        
    return media_group