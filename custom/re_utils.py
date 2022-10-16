import re

def replace_bad_symbols(s):
    """
    Удаление и замена "проблемных" символов.
    """
    s = s.replace('/\n', '   ')
    s = s.replace('\t', '  ')
    s = s.replace('ё', 'е')
    return s

def main_re(s):
    """
    Удаление лишних символов, за исключением <, >, +.
    """
    return re.sub(r'[^\w\s\+\<\>]',' ', s)

def digit_add_spaces_re(s):
    """
    Добавление пробелов между цифрой и любым символом.
    """
    return re.sub('(\d+(\.\d+)?)', r' \1 ', s).strip()

def spaces_re(s): 
    """
    Удаление множественных пробелов.
    """
    s = re.sub(" +", " ", s)
    return re.sub(r"^\s+|\s+$", "", s)

def digit_remove_spaces_re(s):
    """
    Убрать все пробелы между цифрами.
    """
    return re.sub('(?<=\d) (?=\d)', '', s)

def check_phone(s):
    possible_dig = ''
    p = re.compile('((\+7)(9|g|q)(\d|i|o|з|о|l|j|z|ч|б|b|ь|q|g){9})')
    s = p.sub('<phone>', s) 
    return s

# def check_phone(s):
#     possible_dig = ''
#     p = re.compile('(([^\d\+]+)((8|\+7|7)?(9|g|q)(\d|i|o|з|о|l|j|z|ч|б|b|ь|q|g){9})([^\d]))')
#     s = p.sub(r'\2<phone>\7', s) 
#     return s

def replace_double_symbols(s):
    """
    Избавляется от одного/двух символов между цифрами. Примеры: '8 . 9 . 1', '8 aa 9 aa 1'. 
    Применять после функции digit_add_spaces_re, чтобы пробелы были гарантированно.
    """
    p = re.compile('(\s([^(\s|\d){1,2}])\s)')
    s = p.sub(' ', s)
    return s 

def check_mail(s):
    if all([v not in s for v in ['.ru','.ру','.рф','.ком','.орг','.нет','.rf','.net','.net','.be','.com','.org','.me']]):
        return s
    p = re.compile('((\w|\d|\_)+)(@+)((\w|\_|\d)*)(\.)((ru|ру|рф|ком|орг|нет|rf|net|net|be|com|org|me)+)')
    s = p.sub('<mail>', s) 
    return s

def check_tg_inst(s):
    p = re.compile('(\s@\w+(\w|\d|\_){2,})')
    s = p.sub('<tg_inst>', s)
    return s

def check_site(s):
    if all([v not in s for v in ['.ru','.ру','.рф','.ком','.орг','.нет','.rf','.net','.net','.be','.com','.org','.me']]):
        return s
    p = re.compile('(((http://|https://)?)(www\.)?((\w|\d|\_\-)+\.)((ru|ру|рф|ком|орг|нет|rf|net|net|be|com|org|me)+)(\/[^\s]+)+)')
    s = p.sub('<site>', s)
    return s

def add_spaces_to_tokens(s):
    if all([v not in s for v in ['<phone>', '<mail>', '<tg_inst>', '<site>']]):
        return s
    return spaces_re(re.sub('([^\s]*)(<phone>|<mail>|<tg_inst>|<site>)([^\s]*)',r'\1 \2 \3', s))

def make_special_tokens(s):
    """
    Основная функция замены паттернов тел номера, сайта, ника и почты на соответствующие ключевые слова (токены):
    '<phone>', '<mail>', '<tg_inst>', '<site>'.
    """
    s = f' {s} '
    
    s = check_phone(s)
    s = check_mail(s)
    s = check_tg_inst(s)
    s = check_site(s)
    
    return s.strip()