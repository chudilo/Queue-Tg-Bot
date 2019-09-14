import requests
import json
import random

excuses = ('Что-то пошло не так...',
            'Мне лень...',
            'Рут не дописан...',
            'А может лучше в памп поиграем?',
            '*Смешная фраза для ответа на непредвиденные команды*',
            'Ачивки тебе за это не дадут')


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
    string = "Количество людей на южке: " + str(info['count_of_people'])
    return string


def startHandler(message, cursor):
    flags = {"presence": False, "setcount": False, "nickname": False }
    try:
        cursor.execute('''INSERT INTO users(nickname, chat_id, flags)
VALUES(?,?)''', ('User Unknown', message['message']['chat']['id'], json.dumps(flags)))
    except Exception as e:
        print("DB insert error")
        print(e)
# DONT LEAVE THAT LIKE THIS !!!!!!!!!!!!!!!!!

    return help_message(), cursor

def handleMessage(message, info, cursor):
    msg_txt = message['message']['text']
    chat_id = message['message']['chat']['id']
    answer = random.choice(excuses)

    person = cursor.execute('''SELECT flags FROM users WHERE chat_id=?''', (chat_id))
    flags = cursor.fetchone()
    print("Here flags:")
    print(flags)

    if '/start' in msg_txt:
        answer, cursor = startHandler(message, cursor)

    elif '/help' in msg_txt:
        answer = help_message()

    elif '/info' in msg_txt:
        answer = info_message(inf)

    elif '/setcount' in msg_txt:
        cursor
        answer =
        pass
'''
    elif '/come' in msg_txt:
        #sendMessage(chat_id, help_message())
        pass

    elif '/leave' in msg_txt:
        #Убрать из списка
        pass
'''

    else:
        answer = random.choice(excuses)

    return {'chat_id': chat_id, 'text': answer},  info
