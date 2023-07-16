

# any
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
    b = slice_str(message, 'phone number:','Configuration').strip()
    print(f'вырезаный телефон ', b)
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