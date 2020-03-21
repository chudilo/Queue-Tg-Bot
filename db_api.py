# -*- encoding: utf-8 -*-
import psycopg2
import sys
import datetime
from itertools import chain
from collections import Counter
import re

class DataBase(object):
    def __init__(self, database, user, password=""):
        self.connection = psycopg2.connect(database=database,
                                           user=user,
                                           password=password)

    def __exit__(self):
        self.connection.close()

    def getLastId(self):
        cur = self.connection.cursor()
        cur.execute('''SELECT MAX(id) FROM Users;''')
        rows = cur.fetchone()

        if rows[0] is None:
            return 0
        else:
            return rows[0]

    def getQueue(self, chat_id=None):
        cur = self.connection.cursor()
        if not chat_id:
            cur.execute('''SELECT username FROM users INNER JOIN flags
                           ON users.id = flags.id
                           WHERE presence = true;''')
        else:
            cur.execute('''SELECT username FROM users INNER JOIN flags
                           ON users.id = flags.id
                           WHERE presence = true AND chat_id <> %s;''', (chat_id, ))
        rows = cur.fetchall()

        if rows is None:
            return []
        else:
            return rows

    def getCount(self):
        cur = self.connection.cursor()
        cur.execute('''SELECT count FROM State;''')

        result = cur.fetchone()[0]
        #print("getCount", result)
        return result

    def getUserChatId(self, username):
        cur = self.connection.cursor()
        cur.execute('''SELECT chat_id FROM users WHERE username = %s;''', (username, ))

        print("here")
        result = cur.fetchone()[0]
        print("getUserChatId", result)

        return result

    def getLastUpdate(self):
        cur = self.connection.cursor()
        cur.execute('''SELECT last_update FROM State;''')

        result = cur.fetchone()[0]
        print("getCount", result)
        return result

    def getFlag(self, chat_id, flag):
        cur = self.connection.cursor()
        query = '''SELECT {} FROM flags
                   WHERE id = (SELECT id FROM users WHERE chat_id = %s);
                '''.format(flag)
        cur.execute(query, (chat_id, ))

        return cur.fetchone()[0]

    def getNickName(self, chat_id):
        cur = self.connection.cursor()
        cur.execute('''SELECT username FROM users WHERE chat_id = %s;''', (chat_id, ))

        result = cur.fetchone()[0]

        return result

    def getNicknames(self):
        cur = self.connection.cursor()
        cur.execute('''SELECT username FROM Users;''')

        rows = cur.fetchall()

        print(rows)
        return [row[0] for row in rows]

    def initTables(self):
        cur = self.connection.cursor()

        cur.execute('''CREATE TABLE Users
        (id INT PRIMARY KEY,
        chat_id INT NOT NULL CONSTRAINT Users_unique_chat_id UNIQUE,
        username VARCHAR(40) NOT NULL CONSTRAINT Users_unique_username UNIQUE
        );
        ''')

        cur.execute('''CREATE TABLE Flags
        (id INT PRIMARY KEY NOT NULL REFERENCES Users ON DELETE CASCADE,
        presence BOOL NOT NULL DEFAULT false,
        set_count BOOL NOT NULL DEFAULT false,
        nickname BOOL NOT NULL DEFAULT true,
        shadow_ban BOOL NOT NULL DEFAULT false
        );
        ''')

        cur.execute('''CREATE TABLE Messages
        (id SERIAL PRIMARY KEY,
        user_id INT NOT NULL REFERENCES Users(chat_id),
        tg_name VARCHAR(40),
        tg_id VARCHAR(40),
        content TEXT NOT NULL,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        ''')

        cur.execute('''CREATE TABLE State
        (count SMALLINT NOT NULL DEFAULT 0 CHECK (count >= 0),
        last_update TIMESTAMP DEFAULT NULL);''')

        cur.execute('''INSERT INTO State Values(DEFAULT);''')

        self.connection.commit()

    def createUser(self, chat_id, username="Радостный пользователь"):
        cur = self.connection.cursor()

        new_index = self.getLastId() + 1

        cur.execute('''INSERT INTO Users (id, chat_id, username) VALUES (%s, %s, %s);''',
                    (new_index, chat_id, username))

        cur.execute('''INSERT INTO Flags(id) VALUES(%s);''', (new_index,))

        self.connection.commit()

    def writeMessage(self, user_id, tg_name, tg_id, content):
        cur = self.connection.cursor()
        cur.execute('''INSERT INTO Messages (user_id, tg_name, tg_id, content) VALUES (%s, %s, %s, %s);''',
                    (user_id, tg_name, tg_id, content,))

        self.connection.commit()

    # method returns is flag was changed
    def setUserFlag(self, user_id, flag):
        result = not self.getFlag(user_id, flag)

        cur = self.connection.cursor()
        query = '''UPDATE flags SET {} = true 
                   WHERE id = (SELECT id FROM users WHERE chat_id = %s);
                '''.format(flag)

        cur.execute(query, (user_id, ))
        self.connection.commit()

        return result

    # method returns is flag was changed
    def clrUserFlag(self, user_id, flag):
        result = self.getFlag(user_id, flag)

        cur = self.connection.cursor()
        query = '''UPDATE flags SET {} = false 
                   WHERE id = (SELECT id FROM users WHERE chat_id = %s);
                '''.format(flag)

        cur.execute(query, (user_id, ))
        self.connection.commit()

        return result

    def getUser(self, chat_id):
        cur = self.connection.cursor()

        cur.execute('''SELECT id FROM Users WHERE chat_id=%s;''', (chat_id, ))

        val = cur.fetchone()
        return val

    def setCount(self, count):
        cur = self.connection.cursor()

        cur.execute('''UPDATE State SET count=%s, last_update = CURRENT_TIMESTAMP ;''', (count, ))
        self.connection.commit()

    def incCount(self):
        cur = self.connection.cursor()

        cur.execute('''UPDATE State SET count=count+1, last_update = CURRENT_TIMESTAMP ;''')
        self.connection.commit()

    def decCount(self):
        cur = self.connection.cursor()

        cur.execute('''UPDATE State SET count=count-1, last_update = CURRENT_TIMESTAMP ;''')
        self.connection.commit()

    def setNickname(self, chat_id, new_nickname):
        cur = self.connection.cursor()

        cur.execute('''UPDATE Users SET username=%s
                       WHERE chat_id = %s;''', (new_nickname, chat_id, ))
        self.connection.commit()

    def resetNight(self):
        cur = self.connection.cursor()

        cur.execute('''UPDATE Flags SET presence = false;''')
        cur.execute('''UPDATE State SET count = 0;''')
        cur.execute('''UPDATE State SET last_update = NULL''')
        self.connection.commit()

    def getWeekDays(self, chat_id):
        cur = self.connection.cursor()

        cur.execute('''SELECT DISTINCT CAST(time AS DATE) FROM messages WHERE content = '/come' AND
                        user_id = %s;''', (chat_id, ))

        days = cur.fetchall()
        if days:
            days = [day[0] for day in days]
            return days
        else:
            return []

    def getWeekDaysName(self, username):
        cur = self.connection.cursor()

        cur.execute('''SELECT DISTINCT CAST(time AS DATE) FROM messages WHERE content = '/come' AND
                        user_id = (SELECT chat_id FROM users WHERE username = %s);''', (username, ))

        days = cur.fetchall()
        if days:
            days = [day[0] for day in days]
            return days
        else:
            return []

        """
        cur.execute('''SELECT time FROM messages WHERE content='/come' AND 
                            user_id=(SELECT chat_id FROM users WHERE username=%s);''', (username, ))

        days = cur.fetchall()
        print(days)
        days = [day[0].weekday() for day in days]

        days_names = ('пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс')
        week = [(days_names[i], days.count(i)) for i in range(7)]

        return week
        """
    def getAllChatId(self):
        cur = self.connection.cursor()

        cur.execute('''SELECT chat_id FROM users;''')

        return [item[0] for item in cur.fetchall()]

    def getAllBotMessages(self):
        cur = self.connection.cursor()

        cur.execute('''SELECT content, time FROM messages
                       WHERE tg_name='PUMP_BOT' OR tg_id='TgBot';''')

        return cur.fetchall()


def getDayCount(message):
    inf = re.findall(r'Количество людей на южке: \d+|Количество людей на локации: \d+', message)
    if inf:
        return int(re.findall(r'\d+', inf[0])[0])
    else:
        return 0

def getMsgs():
    db = DataBase("pump_bot", "chudik")
    messages = db.getAllBotMessages()
    # print(len(messages))
    dated_messages = dict()

    for message in messages:
        ord = message[1].toordinal()
        if ord not in dated_messages.keys():
            dated_messages[ord] = [message[0]]
        else:
            dated_messages[ord].append(message[0])

    for key in dated_messages:
        max_count = 0
        for message in dated_messages[key]:
            today_count = getDayCount(message)
            if 20 > today_count > max_count:
                max_count = today_count
        dated_messages[key] = max_count

    graph = {'day': [], 'counter': []}
    for key in dated_messages.keys():
        graph['day'].append(datetime.date.fromordinal(key))
        graph['counter'].append(dated_messages[key])

    return graph

def getStat():
    db = DataBase("pump_bot", "chudik")

    all_chat_id = db.getAllChatId()

    # datetime.datetime(2019, 9, 21) + datetime.timedelta(days=1)

    all_days = [list(map(datetime.datetime.toordinal, db.getWeekDays(id))) for id in all_chat_id]
    counter = Counter(list(chain.from_iterable(all_days)))
    graph = {'day': [], 'counter': []}
    for key in counter.keys():
        graph['day'].append(datetime.date.fromordinal(key))
        graph['counter'].append(counter[key])

    day = graph['day'][0]
    while day < datetime.date.today():
        if day not in graph['day']:
            i = graph['day'].index(day - datetime.timedelta(days=1))
            graph['day'].insert(i + 1, day)
            graph['counter'].insert(i + 1, 0)

        day += datetime.timedelta(days=1)

    # graph = [[datetime.date.fromordinal(key)], counter[key]] for key in counter.keys()]


    return graph


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            db = DataBase("test", "ubuntu")
            db.initTables()

        elif sys.argv[1] == 'reset':
            db = DataBase("pump_bot", "ubuntu")
            db.resetNight()

        else:
            print("Wrong arguments; try: 'init', 'reset'")

    else:
        print("Need arguments; try: 'init', 'reset'")


if __name__ == '__main__':
    main()
