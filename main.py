import requests
import json
import time
import logging

from mytgapi import getMe, getUpdates, sendMessage, answerMessage

format = """%(asctime)s ~~~ %(message)s
----------------------------------------------
"""

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


def main():
    #logging.warning("This is warning test log")
    info = None #has count_of_people, people and update_id fields
    try:
        info = Info(INFONAME)
    except Exception as e:
        print('here')
        #logging.warning("INFO OPEN BLOCK\n" + str(e.__class__) + '\n' + str(e))
        logging.warning(e)
        exit()
    
    while True:
        try:
            messages = getUpdates(info.update_id)
            if messages['result']:
                for message in messages['result']:
                    try:
                        print(message['message']['text'])
                        response, info = answerMessage(message, info)
                        try:
                            print(response['text'])
                            sendMessage(response['chat_id'], response['text'])
                        except Exception as e:
                            logging.warning("ANSWERING BLOCK\n" + str(e.__class__) + '\n' + e)

                    except Exception as e:
                        #log("RESPONSE FORM BLOCK\n" + str(e.__class__) + '\n' + str(e), {'chat_id': message['message']['chat']['id'], 'text': message['message']['text']})
                        logging.warning(e)
                        info.update_id += 1
                    finally:
                        info.save(INFONAME)



        except Exception as e:
            #logging.warning("REQUEST BLOCK\n" + str(e.__class__) + '\n' + e)
            logging.warning(e)

        time.sleep(2)


if __name__ == '__main__':
    #print(getMe())
    main()
