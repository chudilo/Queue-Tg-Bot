import requests
import json
import time
import logging

from mytgapi import getMe, getUpdates, sendMessage, answerMessage

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logging.log',level=logging.DEBUG)

def main():
    count_of_people = None
    update_id = None
    inf = None

    with open('info.conf', 'r') as f:
        inf = json.load(f)
        count_of_people = inf['count_of_people']
        update_id = inf['update_id']

    while True:
        try:
            resp = getUpdates(update_id)
            print(json.dumps(resp, indent=4))
            if resp['result']:
                for message in resp['result']:
                    #text = 'Ты написал мне ' + message['message']['text'].strip().lower()
                    answer, inf = answerMessage(message, inf)
                    sendMessage(message['message']['chat']['id'], answer)

                update_id = resp['result'][-1]['update_id'] + 1

                with open('info.conf', 'w') as f:
                    inf['update_id'] = update_id
                    json.dump(inf, f, indent=4)

            else:
                pass
        except Exception as e:
            print(e.__class__)
            logging.warning(e)

        time.sleep(2)



if __name__ == '__main__':
    #print(getMe())
    main()
