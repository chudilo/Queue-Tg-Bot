import requests
import json
import time
import logging
import sqlite3
import datetime

from mytgapi import getMe, getUpdates, sendMessage, handleMessage, Info


def connectDB():
    db = sqlite3.connect('data/UserDB')
    try:
        db.cursor().execute('''CREATE TABLE users(id INTEGER PRIMARY KEY,
                            nickname TEXT, chat_id TEXT, flags TEXT)
                            ''')
        db.commit()
    except Exception as e:
        logging.exception(e)

    return db


def connectLogDB():
    db_log = sqlite3.connect('data/log.db')

    try:
        db_log.cursor().execute('''CREATE TABLE log(id INTEGER PRIMARY KEY,
                           chat_id TEXT, username TEXT, text TEXT, time TEXT)
                           ''')
        db_log.commit()
    except Exception as e:
        logging.exception(e)

    return db_log


def logMessageDB(database, message, text=None):
    if text:
        database.cursor().execute('''INSERT INTO log
        (chat_id, username, text, time) VALUES(?,?,?,?)''',
                        (message['message']['chat']['id'],
                         "TgBot",
                         text,
                         message['message']['date'])
                         )

    else:
        database.cursor().execute('''INSERT INTO log
        (chat_id, username, text, time) VALUES(?,?,?,?)''',
                        (message['message']['chat']['id'],
                         message['message']['chat']['username'],
                         message['message']['text'],
                         message['message']['date'])
                         )
    database.commit()

LOG_EXCEPTIONS = 'logging.log'
format = """
----------------------------------------------
%(asctime)s ~~~
%(message)s"""
logging.basicConfig(format=format, datefmt='%m/%d/%Y %I:%M:%S %p', filename=LOG_EXCEPTIONS,level=logging.WARNING)

INFONAME = 'info.conf'


def main():
    db = connectDB()
    db_log = connectLogDB()

    info = None
    try:
        info = Info(INFONAME)
    except Exception as e:
        logging.exception(e)
        exit()

    while True:
        try:
            #messages = getUpdates(info.update_id)
            messages = {'result':  [{"message": {'date': "1377", 'text': input(), 'chat': {'id': 100500, 'username': "LOCALTEST"}}}]}
            if messages['result']:
                for message in messages['result']:
                    try:
                        #print(message['message']['text'])
                        logMessageDB(db_log, message)
                        response, new_info = handleMessage(message, info, db)

                        #print(response['text'])
                        logMessageDB(db_log, message, text=response['text'])
                        sendMessage(response['chat_id'], response['text'])

                        info = new_info
                    except Exception as e:
                        logging.exception(e)

                    finally:
                        info.update_id += 1
                        info.save(INFONAME)

        except Exception as e:
            logging.exception(e)
        time.sleep(2)


if __name__ == '__main__':
    main()
