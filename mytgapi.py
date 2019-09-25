import requests
import json
import random
import logging
import datetime

import datetime


class Info(object):
    def __init__(self, filename):
        with open(filename, 'r') as f:
            info = json.load(f)
            self.count_of_people = int(info['count_of_people'])
            self.people = info['people']
            self.update_id = int(info['update_id'])
            self.last_update = datetime.datetime.strptime(info['last_update'], "%Y-%m-%d %H:%M:%S.%f")

    def save(self, filename):
        with open(filename, 'w') as f:
            info = {'count_of_people' : self.count_of_people,
                'people' : self.people,
                'update_id': self.update_id,
                'last_update': str(self.last_update)}
            json.dump(info, f, indent=4)


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


def sendMessage(chat_id, text="Test message", numbers=False):
    url = URL + '/sendMessage'
    r = None
    if not numbers:
        r = requests.post(url, json={'chat_id': chat_id, 'text': text,
            'reply_markup':{"resize_keyboard": true, "keyboard":
                [[{"text": "/help"}, {"text": "/nick"}, {"text": "/info"}],
                [{"text": "/come"}, {"text": "/leave"}],
                [{"text": "/setcount"}]]} })
    else:
        r = requests.post(url, json={'chat_id': chat_id, 'text': text,
            'reply_markup':{"resize_keyboard": true, "keyboard":
                [[{"text": "1"}, {"text": "2"}, {"text": "3"}],
                [{"text": "4"}, {"text": "5"}, {"text": "6"}],
                [{"text": "7"}, {"text": "8"}, {"text": "9"}],
                [{"text": "0"}]]}

    return r.json()


def getMe():
    url = URL + '/getMe'
    r = requests.get(url)
    return r.json()


def help_message():
    string = """Uzka Queue Bot v1.1.4\nИзвините, я упячко (I will fix it, probably)
    /help - вывести список команд
    /info - узнать количество человек на южке
    /nick - задать себе имя
    /setcount - задать количество человек на локации
    /come - приехать на южку
    /leave - уехать с южки

По всем вопросам неопределенного поведения писать @chudikchudik"""
    return string

def isNickInDB(new_nick, db):
    people = db.cursor().execute('''SELECT nickname FROM users''').fetchall()
    for nick in people:
        if nick[0] == new_nick:
            return True
    return False


def isUpdateOld(info):
    new = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    upd = info.last_update
    old = None
    if new.day != upd.day:
        if new.hour > 1:
            old = True
        else:
            if (new-upd).days == 0 and upd.hour > 1:
                old = False
            else:
                old = True
    else:
        if upd.hour > 1 or (new-upd).seconds <= 3600:
            old = False
        else:
            old = True

    return old


def resetNight(info, db):
    info.count_of_people = 0
    info.people = []
    persons_flag = db.cursor().execute('''SELECT chat_id, flags FROM users''')
    for person in persons_flag:
        new_flags = json.loads(person[1])
        new_flags['presence'] = False
        db.cursor().execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(new_flags), person[0]))
    db.commit()

    return info


def list_of_people(info, db):
    people = db.cursor().execute('''SELECT nickname, flags FROM users''').fetchall()
    str_lst = ""
    count = int(info.count_of_people)
    for person in people:
        if person[0] != "User Unknown" and json.loads(person[1])['presence']:
            str_lst += str(person[0]) + "; "
            count -= 1
    if count not in (0, 1, 2, 3, 4, 21):
        str_lst += str(count) + " рандомов."
    elif count in (1, 21):
        str_lst += str(count) + " рандом."
    elif count in (2, 3, 4):
        str_lst += str(count) + " рандома."

    return str_lst

#with nicks
def num_of_people(info, db):
    people = db.cursor().execute('''SELECT nickname, flags FROM users''').fetchall()
    count = 0
    for person in people:
        if json.loads(person[1])['presence']:
            count += 1

    return count


def update_time(info):
    if isUpdateOld(info):
        return ""
    else:
        return "\nПоследнее обновление: " + info.last_update.strftime("%H:%M")


def info_message(info, db):
    str_count = "Количество людей на южке: " + str(info.count_of_people)

    str_people = ""
    if info.count_of_people:
        str_people = "\n" + list_of_people(info, db)

    str_update = update_time(info)

    return str_count + str_people + str_update
    '''
    if info.people:
        string += "\n"
        for person in info.people:
            string += person + "; "
        string += str(info.count_of_people - len(info.people)) + " рандома"

    if not isUpdateOld:
        #print("Hmmm")
        string += "\n" + info_message_time(info)
    #else:
        #print("AAAAAAAAA")
    return string
    '''

def info_message_time(info):
    return "Последне обновление: " + info.last_update.strftime("%H:%M")

    '''
    delt = datetime.datetime.utcnow() + datetime.timedelta(hours=3) - info.last_update
    print(delt, delt.seconds/3600, delt.days)
    #print(delt.seconds, delt.days)
    if delt.seconds/3600 < 9 and not delt.days:
        return "Последне обновление: " + info.last_update.strftime("%H:%M")
    else:
        print("OhWow")
        return None
    '''

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

def handleMessage(message, info, db):
    cursor = db.cursor()
    num = False
    msg_txt = message['message']['text']
    chat_id = message['message']['chat']['id']
    answer = random.choice(excuses)

    #person = cursor.execute('''SELECT flags FROM users WHERE chat_id=?''', (chat_id, ))
    #flags = cursor.fetchone()
    #if flags:
    #    flags = json.loads(flags[0])
    #flags = {"presence": False, "setcount": False, "nickname": False}
    #print(flags)

    #print("before reset")
    if isUpdateOld(info):
        info = resetNight(info, db)

    #print("After reset")
    person = cursor.execute('''SELECT flags FROM users WHERE chat_id=?''', (chat_id, ))
    flags = cursor.fetchone()
    if flags:
        flags = json.loads(flags[0])
    #print(flags)

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
        #print("FIRST CHECK")
        if '/info' in msg_txt:
        #    print("AAAAA")
            answer = info_message(info, db)

        elif '/setcount' in msg_txt:
            if not flags['setcount']:
                num = True
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
                    if num < num_of_people(info, db):
                        answer = "Я чувствую подвох. Уровень искуственного интеллекта на земле еще не настолько развит, чтобы понять, сколько людей сейчас на южке"
                    else:
                        info.count_of_people = num
                        info.last_update = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                        answer = info_message(info, db)
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
            #print("CHECK TWO")
            nick = msg_txt.strip()
            if len(nick) <= 10:
                if nick[0] != '/':
                #print("GOOD NICK BLOCK~~~~")
                    if not isNickInDB(nick, db):
                        cursor.execute('''UPDATE users SET nickname=? WHERE chat_id=?''', (nick, chat_id,))
                        answer = "Приветствую, " + nick + "!"
                    else:
                        answer = "Этот ник уже был."
                else:
                    answer = "Лучше так не делать."
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
                #print(nick)
                if nick == "User Unknown":
                #    info.people.append(nick)
                    answer = "Добро пожаловать. Снова."
                else:
                    answer = "Добро пожаловать, " + str(nick) + ". Снова."
                answer += "\n\n" + info_message(info,db)

        elif '/leave' in msg_txt:
            if not flags['presence']:
                answer = "Но ты же еще не приехал...("
            else:
                info.count_of_people -= 1
                info.last_update = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                flags['presence'] = False
                cursor.execute('''UPDATE users SET flags=? WHERE chat_id=?''', (json.dumps(flags),chat_id,))
                nick = cursor.execute('''SELECT nickname FROM users WHERE chat_id=?''', (chat_id, )).fetchone()[0]
                '''
                print(nick)
                if nick != "User Unknown":
                    try:
                        info.people.remove(nick)
                    except Exception as e:
                        logging(e)
                '''
                answer = "Будем ждать тебя!"
                answer += "\n\n" + info_message(info, db)

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
    db.commit()
    return {'chat_id': chat_id, 'text': answer},  info, num
