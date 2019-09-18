import requests
import json
import random
import logging
import datetime

import datetime

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
    string = "Uzka Queue Bot v1.1\nИзвините, я упячко (I will fix it, probably)\n\n"+\
    "/help - вывести список команд;\n" +\
    "/info - узнать количество человек на южке\n\n" +\
    "/nick - задать себе имя\n\n" +\
    "/setcount - задать количество человек на локации\n"+\
    "/come - приехать на южку;\n" +\
    "/leave - уехать с южки;\n"
    return string


def info_message(info):
    string = "Количество людей на южке: " + str(info.count_of_people)
    if info.people:
        string += "\n"
        for person in info.people:
            string += person + "; "
        string += str(info.count_of_people - len(info.people)) + " рандома"
    return string

def info_message_time(info):
    delt = datetime.datetime.utcnow() + datetime.timedelta(hours=3) - info.last_update
    print(delt, delt.seconds/3600, delt.days)
    #print(delt.seconds, delt.days)
    if delt.seconds/3600 < 9 and not delt.days:
        return "Последне обновление: " + info.last_update.strftime("%H:%M")
    else:
        print("OhWow")
        return None


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
    #flags = {"presence": False, "setcount": False, "nickname": False}
    print(flags)
    
    if '/start' in msg_txt:
        if not flags:
            startHandler(message, cursor)
        answer = help_message()

    elif '/help' in msg_txt:
        answer = help_message()

    #time = datetime.datetime.utcnow()

    elif datetime.datetime.utcnow().hour < 7 or datetime.datetime.utcnow().hour > 21:
        info.count_of_people = 0
        answer = "Южка спит и детки спят\nЗавтра пампить захотят."
    else:
        print("FIRST CHECK")
        if '/info' in msg_txt:
            answer = info_message(info)
            add = info_message_time(info)
            if add != None:
                answer += "\n" + info_message_time(info)
            else:
                answer += "\nДавно-давно..."
                info.count_of_people = 0
                info.people = []
                persons_flag = cursor.execute('''SELECT chat_id, flags FROM users''')
                for person in persons_flag:
                    new_flags = json.loads(person[1])
                    new_flags['persence'] = False
                    cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(new_flags), person[0]))

        elif '/setcount' in msg_txt:
            if not flags['setcount']:
                flags['setcount'] = True
                cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
                answer = "Напишите, сколько людей сейчас на локации:"
            else:
                answer = "Напишите, сколько людей сейчас на локации:"

        elif flags['setcount']:
            flags['setcount'] = False
            cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
            if msg_txt.strip().isdigit():
                num = int(msg_txt.strip())
                if 0 <= num <= 25:
                    if num < len(info.people):
                        answer = "Я чувствую подвох. Уровень искуственного интеллекта на земле еще не настолько развит, чтобы понять, сколько людей сейчас на южке"
                    else: 
                        info.count_of_people = num
                        info.last_update = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                        answer = info_message(info)
                else:
                    answer = "Я программист, меня не обманешь..."
            else:
                answer = "Неправильный формат ввода"

        elif '/nick' in msg_txt:
            if not flags['nickname']:
                flags['nickname'] = True
                cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
                answer = "Напишите ваш новый ник:"
            else:
                answer = "Этот кусок кода заставил меня залипнуть минут на 10\nНапишите ваш новый ник:"

        elif flags['nickname']:
            flags['nickname'] = False
            cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
            print("CHECK TWO")
            nick = msg_txt.strip()
            if len(nick) <= 10 and nick[0] != '/':
                print("GOOD NICK BLOCK~~~~")
                cursor.execute('''UPDATE users SET nickname=? WHERE chat_id=?''', (nick, chat_id,))
                answer = "Приветствую, " + nick + "!"
            else:
                answer = "Слишком большой! (макс. 10 символов)"

        elif '/come' in msg_txt:
            if flags['presence']:
                answer = "Я знаю, что ты здесь)"
            else:
                info.count_of_people += 1
                info.last_update = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                flags['presence'] = True
                cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))

                nick = cursor.execute('''SELECT nickname FROM users WHERE chat_id=?''', (chat_id, )).fetchone()[0]
                print(nick)
                if nick != "User Unknown":
                    info.people.append(nick)
                
                answer = "Добро пожаловать. Снова."

        elif '/leave' in msg_txt:
            if not flags['presence']:
                answer = "Но ты же еще не приехал...("
            else:
                info.count_of_people -= 1
                info.last_update = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                flags['presence'] = False
                cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
                nick = cursor.execute('''SELECT nickname FROM users WHERE chat_id=?''', (chat_id, )).fetchone()[0]
                print(nick)
                if nick != "User Unknown":
                    info.people.remove(nick)

                answer = "Будем ждать тебя!"

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
