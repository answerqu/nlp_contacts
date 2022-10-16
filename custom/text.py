import re
import os
import json
from nltk.corpus import stopwords
import pymorphy2
import pandas as pd

from .load_dicts import load_first_dict, load_second_dict, load_third_dict
from .re_utils import (replace_bad_symbols, main_re, digit_add_spaces_re, 
                        digit_remove_spaces_re, spaces_re, make_special_tokens, replace_double_symbols, 
                        add_spaces_to_tokens, check_phone)


class TextPreprocessor:
    """
    Класс полной обработки текста, который в дальнейшем может передаваться в модель обучения.

    Args:
        dict_normal - словарь перевода слов в его числовой аналог.
        morph - объект класса pymorphy.MorphAnalyzer().
        max_len - максимальное количество слов (токенов) в тексте. Текст преобразуется по следубщему правилу: 
                  первые max_len//2-1 слов + связующий токен + последние max_len//2.
    """
    def __init__(self, dict_normal = {}, morph = None, max_len = 1000) -> None:
        self.dict_normal = {}
        self.morph = pymorphy2.MorphAnalyzer() if morph is None else morph
        self.max_len = max_len

        if os.path.exists('lib/utils/stopwords.json'):
            with open('lib/utils/stopwords.json', 'r+') as f:
                self.stopwords = json.load(f)
        else:
            self.stopwords = []
    
    @staticmethod
    def first_replacement(df) -> pd.DataFrame:
        """
        Функция заменяет в датафрейме подстроки типа "три ноля", "пять единиц" на их цифровые аналоги -> "000", "11111".
        Реализация создания всевозможных вариантов подстрок представлена в функции load_dicts.load_first_dict.
        """
        counts_dict, dig_dict = load_first_dict()

        for count_name, count in counts_dict.items():
            sample_c = df[df.text.str.find(count_name) != -1]
            if sample_c.shape[0] == 0:
                continue

            for dig_name, dig in dig_dict.items(): 
                sample_d = sample_c[sample_c.text.str.find(dig_name) != -1]
                if sample_d.shape[0] == 0:
                    continue
        
                set_of_strings = []
                for space in range(0,2):
                    set_of_strings.append(count_name + ' '*space + dig_name)
                set_of_strings = set(set_of_strings)

                for s in set_of_strings:
                    sample_tmp = sample_d[sample_d.text.str.find(s) != -1]

                    if sample_tmp.shape[0] != 0:
                        df.loc[sample_tmp.index, 'text'] = sample_tmp.text.str.replace(s, count*dig).values
                        sample_c.loc[sample_tmp.index, 'text'] = sample_tmp.text.str.replace(s, count*dig).values
                        sample_d.loc[sample_tmp.index, 'text'] = sample_tmp.text.str.replace(s, count*dig).values
        
        return df
    
    @staticmethod
    def second_replacement(df) -> pd.DataFrame:
        """
        Функция заменяет в датафрейме подстроки типа "девятьсот тринадцать", "восемьдесят пять" на их цифровые аналоги -> "913", "85".
        Реализация создания всевозможных вариантов подстрок представлена в функции load_dicts.load_second_dict.
        """
        ones, tens, hundreths = load_second_dict()

        for h, h_val in hundreths.items():
            sample_h = df[df.text.str.find(h) != -1]
            if sample_h.shape[0] == 0:
                continue

            for t, t_val in tens.items():
                sample_t = sample_h[sample_h.text.str.find(t) != -1]
                if sample_t.shape[0] == 0:
                    continue
                
                for o, o_val in ones.items():
                    sample_o = sample_t[sample_t.text.str.find(o) != -1]
                    if sample_o.shape[0] == 0:
                        continue

                    if h+t+o == '':
                        continue

                    if 'дцат' in t and t not in ['двадцать', 'тридцать','двацать', 'трицать', 'двадцат', 'тридцат']:
                        o = ''
                        o_val = 0
                    
                        
                    set_of_strings = []
                    for first_space in range(0,2):
                        for second_space in range(0,2):
                            set_of_strings.append(h + ' '*first_space + t + ' '*second_space + o)
                    set_of_strings = set(set_of_strings)

                    for s in set_of_strings:
                        s = f' {s} ' if s == 'сто' else s
                        sample_tmp = sample_o[sample_o.text.str.find(s) != -1]

                        if sample_tmp.shape[0] != 0:
                            replace_str = f' {str(h_val+t_val+o_val)} ' if s == 'сто' else str(h_val+t_val+o_val)
                            df.loc[sample_tmp.index, 'text'] = sample_tmp.text.str.replace(s, replace_str).values
                            sample_h.loc[sample_tmp.index, 'text'] = sample_tmp.text.str.replace(s, replace_str).values
                            sample_t.loc[sample_tmp.index, 'text'] = sample_tmp.text.str.replace(s, replace_str).values
                            sample_o.loc[sample_tmp.index, 'text'] = sample_tmp.text.str.replace(s, replace_str).values
        
        return df

    @staticmethod                
    def third_replacement(df) -> pd.DataFrame:
        """
        Функция заменяет в датафрейме подстроки типа "восемь", "один" на их цифровые аналоги -> "8", "1".
        Реализация создания всевозможных вариантов подстрок представлена в функции load_dicts.load_third_dict.
        """
        digits_dict = load_third_dict()

        for s, v in digits_dict.items():
            sample = df[df.text.str.find(s) != -1]
            if sample.shape[0] != 0:
                df.loc[sample.index, 'text'] = sample.text.str.replace(s, v).values
        
        return df

    def bad_numbers_handle(self, df) -> pd.DataFrame:
        """
        Функция состоит из двух этапов:
        1. Удаление неинформативных символов, определение "информативных" токенов <phone>, <mail>, <site>, <tg_inst>.
        2. Обработка "хитрых" номеров. Переводит номера типа "8 девятьсот тринадцать сто двадцать три 4567" в строку '89131234567'.
        """
        
        df['text_w_spaces'] = df['description'].str.lower().map(replace_bad_symbols) # тексты колонки по длине совпадают с description
        df['text'] = df.text_w_spaces.map(make_special_tokens).map(digit_add_spaces_re).map(spaces_re).map(main_re).fillna('')
        
        df = self.first_replacement(df)
        df = self.second_replacement(df)
        df = self.third_replacement(df)

        df['text'] = (df['text'].str.replace('девяно10', '9')
                                .str.replace('дцать', '')
                                .str.replace('надцать', '')
                                .str.replace('десят', '')
                                .str.replace(r'\\xa0','', regex=True)) # обработка неучтенных случаев
                    
        df['text'] = (df['text']
                        .str.strip()
                        .map(digit_add_spaces_re)
                        .map(replace_double_symbols)
                        .map(spaces_re)
                        .map(digit_remove_spaces_re)
                        .str.replace('\+ 7', '+7')
                        .str.replace(' + ', '  ')
                        .map(check_phone)
                        .map(add_spaces_to_tokens)) # конечная предобработка строк с цифрами

        return df

    def replace_to_informative_tokens(self, s) -> list:
        """
        Функция замены набора в строке идущих подряд цифр на ключевы токены "{первая цифра}_digits_{количество цифр}". 
        Если же токен является словом, применяется нормализация этого слова библиотекой pymorphy2.
        Функция применима к одному слову (токену).
        """
        normal_form = self.dict_normal.get(s)
        if normal_form is None:
            ss = re.sub('^(\+|id)?\d*$', 'some_digits', s)
            if ss == 'some_digits':
                digits = re.sub('[^\d]','', s)
                if s.replace('id','').isdigit() and 'id' in s: #ВК айди
                    return 'id_digits_{str(len(s)-2)}'
                elif s.replace('+','').isdigit() and '+' in s: #+7 формат
                    return f'plus_{s[1]}_digits_{str(len(s)-1)}'
                else: 
                    return f'<{s[0]}_digits_{str(len(s))}>' #просто цифры (есть формат 89)
            normal_form = self.morph.parse(s)[0].normal_form
            self.dict_normal[s] = normal_form
        return normal_form

    def prepare_word_tokens(self, s) -> list:
        """
        Нормализация и токенизация всего текста.
        """
        s = s.split(' ')
        l = [v for v in s if v != '' and v not in self.stopwords]

        if len(l)> self.max_len:
            l = l[:self.max_len//2-1] + ['<LINK>'] + l[-self.max_len//2:]

        l = [self.replace_to_informative_tokens(s) for s in l]

        return l
        
    def full_text_preprocessing(self, df):
        """
        Функция объединяет в себе предобработку функции bad_numbers_handle, а также нормализацию и токенизацию финального варианта текста.
        """
        df = self.bad_numbers_handle(df) #предобработка текста
        df['normalized_text'] = (df.text.map(self.prepare_word_tokens)
                                .map(lambda x: ' '.join(x)).fillna('')) # нормализация
        df['len_txt']  = df.normalized_text.map(lambda x: len(x))
        df['count_tokens'] = df.description.str.split(' ').map(lambda x: len(x))

        return df