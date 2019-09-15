import requests
import json
import random
import logging

format = """
----------------------------------------------
%(asctime)s ~~~
%(message)s """
LOGNAME = 'logging.log'
logging.basicConfig(format=format, datefmt='%m/%d/%Y %I:%M:%S %p', filename=LOGNAME,level=logging.WARNING)

excuses = ('Я тебя не понимать.',
            'Мне лень...',
            'Рут не дописан...',
            'А может лучше в памп поиграем?',
            '*Смешная фраза для ответа на непредвиденные команды*',
            'Ачивки тебе за это не дадут.')


URL = 'https://api.telegram.org/bot'
with open('token', 'r') as f:
    URL += f.read().strip()


def getUpdates(update_id=1):
    url = URL + '/getUpdates?offset=' + str(update_id)
    r = requests.get(url)
    return r.json()


def sendMessage(chat_id, text="Test message"):
    url = URL + '/sendMessage'
    r = requests.post(url, json={'chat_id': chat_id, 'text': text })
    return r.json()


def getMe():
    url = URL + '/getMe'
    r = requests.get(url)
    return r.json()


def help_message():
    string = "Все команды вводятся в формате /setcount [число]\n" +\
    "Извините, я упячко (I will fix it)\n"+\
    "/help - вывести список команд;\n" +\
    "__/nick - задать себе имя\n" +\
    "__/come - приехать на южку;\n" +\
    "__/leave - уехать с южки;\n" +\
    "/setcount - расскажите, сколько людей сейчас на пампе;\n" +\
    "/info - узнать количество людей;\n"
    return string


def info_message(info):
    string = "Количество людей на южке: " + str(info.count_of_people)
    return string


def startHandler(message, cursor):
    flags = {"presence": False, "setcount": False, "nickname": False }
    try:
        cursor.execute('''INSERT INTO users(nickname, chat_id, flags)
VALUES(?,?,?)''', ('User Unknown', message['message']['chat']['id'], json.dumps(flags)))
    except Exception as e:
        print("~~DB insert error~~")
        print(e)
# DONT LEAVE THAT LIKE THIS !!!!!!!!!!!!!!!!!

    return help_message(), cursor

def handleMessage(message, info, cursor):
    msg_txt = message['message']['text']
    chat_id = message['message']['chat']['id']
    answer = random.choice(excuses)

    person = cursor.execute('''SELECT flags FROM users WHERE chat_id=?''', (chat_id, ))
    flags = cursor.fetchone()
    if flags:
        flags = json.loads(flags[0])

    print("FLAGS:\n")
    print(flags)
    if '/start' in msg_txt:
        if not flags:
            startHandler(message, cursor)
        answer = help_message()

    elif '/help' in msg_txt:
        answer = help_message()

    elif '/info' in msg_txt:
        answer = info_message(inf0)

    elif '/setcount' in msg_txt:
        if not flags['setcount']:
            flags['setcount'] = True
            cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
            answer = "Напишите, сколько людей сейчас на локации:"

    else:
        if flags['setcount']:
            flags['setcount'] = False
            cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
            if msg_txt.strip().isdigit():
                num = int(msg_txt.strip())
                if 0 <= num <= 25:
                    info.count_of_people = num
                    answer = info_message(info)
                else:
                    answer = "Я программист, меня не обманешь..."
            else:
                answer = "Неправильный формат ввода"

        else:
            answer = random.choice(excuses)

    '''
        elif '/come' in msg_txt:
            #sendMessage(chat_id, help_message())
            pass

        elif '/leave' in msg_txt:
            #Убрать из списка
            pass
    '''
    return {'chat_id': chat_id, 'text': answer},  info
