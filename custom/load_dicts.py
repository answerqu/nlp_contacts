import os
import json


def make_first_dict():
    """
    Создание словаря возможных вариантов подстрок типа "три ноля", "пять единиц".
    """
    counts_dict = dict(zip(['два', 'две', 'три', 'четыре','пять', 'шесть', 'восемь', 'семь', 'девять'], [2,2,3,4,5,6,8,7,9]))

    dig_dict = dict(zip([
                        'ноля', 'нуля', 'нулей', 
                        'единиц', 'единицы', 'единичек', 
                        'двойки', 'двоек', 
                        'тройки', 'троек', 
                        'четверок', 'четверки', 
                        'пятерок', 'пятерки', 
                        'шестерок', 'шестерки', 
                        'семерок', 'семерки', 
                        'восьмерок', 'восьмерки', 
                        'девяток', 'девятки'],

                        ['0', '0', '0', 
                        '1', '1', '1', 
                        '2', '2', 
                        '3', '3', 
                        '4', '4', 
                        '5', '5', 
                        '6', '6', 
                        '7', '7', 
                        '8', '8', 
                        '9', '9'],
                        ))
    
    with open('lib/utils/counts.json', 'w+') as f:
        json.dump(counts_dict, f)
    with open('lib/utils/digits.json', 'w+') as f:
        json.dump(dig_dict, f)


def load_first_dict():
    """
    Создание словаря возможных вариантов подстрок типа "девятьсот тринадцать", "восемьдесят пять".
    """
    if not (os.path.exists('lib/utils/counts.json') and os.path.exists('lib/utils/digits.json')):
        make_first_dict()
    
    with open('lib/utils/counts.json', 'r+') as f:
        counts_dict = json.load(f)
    with open('lib/utils/digits.json', 'r+') as f:
        dig_dict = json.load(f)

    return counts_dict, dig_dict


def make_second_dict():
    ones = dict(zip(['один', 'два', 'три', 'четыре','пять', 'шесть', 'семь', 'восемь', 'девять'], range(1,10)))
    del ones['семь']
    ones['семь'] = 7
    ones['восем'] = 8
    ones['сем'] = 7
    
    tens = dict(zip(['двадцать', 'тридцать', 'сорок', 'пятьдесят','шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто'], range(20,91,10)))
    tens['одиннадцать'] = 11
    tens['одинадцать'] = 11
    tens['двенадцать'] = 12
    tens['тринадцать'] = 13
    tens['четырнадцать'] = 14
    tens['пятнадцать'] = 15
    tens['пятьнадцать'] = 15
    tens['шестнадцать'] = 16
    tens['восемнадцать'] = 18
    tens['семнадцать'] = 17
    tens['девятнадцать'] = 19
    tens['восемьдесять'] = 80
    tens['восемдесят'] = 80
    del tens['семьдесят']
    tens['семьдесят'] = 70
    tens['семдесят'] = 70
    tens['шесят'] = 60
    tens['шисят'] = 60
    tens['семьдесять'] = 70
    
    hundreths = dict(zip(['двести', 'триста', 'четыреста','пятьсот', 'шестьсот', 'семьсот', 'восемьсот', 'девятьсот'], range(200,901,100)))
    hundreths['пять сот'] = 500
    hundreths['шесть сот'] = 600
    hundreths['восемь сот'] = 800
    hundreths['семь сот'] = 700
    del hundreths['семьсот']
    hundreths['семьсот'] = 700
    hundreths['девять сот'] = 900
    hundreths['девятсот'] = 900
    hundreths['сто'] = 100
    
    ones[''] = 0
    tens[''] = 0
    hundreths[''] = 0

    
    with open('lib/utils/ones.json', 'w+') as f:
        json.dump(ones, f)
    with open('lib/utils/tens.json', 'w+') as f:
        json.dump(tens, f)
    with open('lib/utils/hundreths.json', 'w+') as f:
        json.dump(hundreths, f)


def load_second_dict():
    if not (os.path.exists('lib/utils/ones.json') and os.path.exists('lib/utils/tens.json') and os.path.exists('lib/utils/hundreths.json')):
        make_second_dict()

    with open('lib/utils/ones.json', 'r+') as f:
        ones = json.load(f)
    with open('lib/utils/tens.json', 'r+') as f:
        tens = json.load(f)
    with open('lib/utils/hundreths.json', 'r+') as f:
        hundreths = json.load(f)
    
    return ones, tens, hundreths

def make_third_dict():
    """
    Создание словаря возможных вариантов подстрок типа "восемь", "один".
    """
    digits_dict = {'ноль': '0', 'нуль': '0', 'один': '1', 'два': '2', 'три': '3', 'четыре': '4', 'четыри': '4', 
                   'пять': '5', 'шесть': '6', 
                   'восемь': '8', 'восем': '8', 'семь': '7', ' сем ': ' 7 ', 'девять': '9', 'девить': '9', 'десять': '10', 
                   'десить': '10', 'десятка': '10'} 
    
    with open('lib/utils/digits_third.json', 'w+') as f:
        json.dump(digits_dict, f)


def load_third_dict():
    if not os.path.exists('lib/utils/digits_third.json'):
        make_third_dict()

    with open('lib/utils/digits_third.json', 'r+') as f:
        digits_dict = json.load(f)

    return digits_dict