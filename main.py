import requests
import json
import time
import logging
import sqlite3

from mytgapi import getMe, getUpdates, sendMessage, handleMessage

format = """
----------------------------------------------
%(asctime)s ~~~
%(message)s """

class Info(object):
    def __init__(self, filename):
        with open(filename, 'r') as f:
            info = json.load(f)
            self.count_of_people = int(info['count_of_people'])
            self.people = info['people']
            self.update_id = int(info['update_id'])

    def save(self, filename):
        with open(filename, 'w') as f:
            info = {'count_of_people' : self.count_of_people,
                'people' : self.people,
                'update_id': self.update_id}
            json.dump(info, f, indent=4)


def log(err_msg, tg_info):
    logging.warning('chat_id:' + str(tg_info['chat_id']) + '; text: ' +
str(tg_info['text']) + '\n' + err_msg)

LOGNAME = 'logging.log'
INFONAME = 'info.conf'
logging.basicConfig(format=format, datefmt='%m/%d/%Y %I:%M:%S %p', filename=LOGNAME,level=logging.WARNING)

db = sqlite3.connect('data/UserDB')
cursor = db.cursor()
try:
    cursor.execute('''
        CREATE TABLE users(id INTEGER PRIMARY KEY, nickname TEXT,
                           chat_id TEXT, flags TEXT)
    ''')
    db.commit()
except Exception as e:
    logging.exception(e)


def main():
    #logging.warning("This is warning test log")
    info = None #has count_of_people, people and update_id fields
    try:
        info = Info(INFONAME)
    except Exception as e:
        #logging.warning("INFO OPEN BLOCK\n" + str(e.__class__) + '\n' + str(e))
        logging.exception(e)
        exit()

    while True:
        try:
            messages = getUpdates(info.update_id)
            print(messages)
            if messages['result']:
                for message in messages['result']:
                    try:
                        print(message['message']['text'])
                        response, new_info, cursor = handleMessage(message, info, cursor)
                        info = new_info
                        try:
                            print(response['text'])
                            sendMessage(response['chat_id'], response['text'])
                        except Exception as e:
                            logging.exception("ANSWERING BLOCK\n" + str(e.__class__) + '\n' + e)

                    except Exception as e:
                        #log("RESPONSE FORM BLOCK\n" + str(e.__class__) + '\n' + str(e), {'chat_id': message['message']['chat']['id'], 'text': message['message']['text']})
                        logging.exception(e)
                        info.update_id += 1
                    finally:
                        info.save(INFONAME)


        except Exception as e:
            #logging.warning("REQUEST BLOCK\n" + str(e.__class__) + '\n' + e)
            logging.exception(e)

        time.sleep(2)


if __name__ == '__main__':
    #print(getMe())
    main()
