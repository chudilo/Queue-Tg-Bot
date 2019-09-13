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
            self.count_of_people = info['count_of_people']
            self.people = info['people']
            self.update_id = info['update_id']

    def save(self, filename):
        with open(filename, 'w') as f:
            info = {'count_of_people' : self.count_of_people,
                'people' : self.people,
                'update_id': self.update_id}
            json.dump(info, f, indent=4)


LOGNAME = 'logging.log'
logging.basicConfig(format=format, datefmt='%m/%d/%Y %I:%M:%S %p', filename=LOGNAME,level=logging.DEBUG)


def main():
    info = None #has count_of_people, people and update_id fields
    try:
        info = Info(LOGNAME)
    except Exception as e:
        logging.warning("INFO OPEN BLOCK\n" + str(e.__class__) + '\n' + str(e))
        exit()

    while True:
        try:
            messages = getUpdates(update_id)
            if messages:
                for message in messages:
                    try:
                        response, info = answerMessage(message, info)
                        try:
                            sendMessage(response['chat_id'], response['text'])
                        except Exception as e:
                            logging.warning("ANSWERING BLOCK\n" + str(e.__class__) + '\n' + str(e))

                    except Exception as e:
                        logging.warning("RESPONSE FORM BLOCK\n" + str(e.__class__) + '\n' + str(e))
                        info.update_id += 1
                    finally:
                        info.save(LOGNAME)



        except Exception as e:
            logging.warning("REQUEST BLOCK\n" + str(e.__class__) + '\n' + str(e))

        time.sleep(2)


if __name__ == '__main__':
    #print(getMe())
    main()
