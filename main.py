import requests
import json
import time

URL = 'https://api.telegram.org/bot'
with open('token', 'r') as f:
    URL += f.read().strip()


def getUpdates(update_id=1):
    url = URL + '/getUpdates?offset=' + str(update_id)
    r = requests.get(url)
    return r.json()


def sendMessage(chat_id, text="Test message"):
    url = URL + '/sendMessage'
    r = requests.post(url, json={'chat_id': chat_id, 'text': text})
    return r.json()


def getMe():
    url = URL + '/getMe'
    r = requests.get(url)
    return r.json()


def answerMessage(message, info):
    msg_txt = message['message']['text']
    
    if '/start' in msg_txt:
        #Предложить выбрать никнейм
        pass
    
    elif '/help' in msg_txt:
        #Вывести список команд
	pass
    
    elif '/come' in msg_txt:
	#Добавить в список
	pass

    elif '/leave' in msg_txt:
	#Убрать из списка
	pass


    elif '/info' in msg_txt:
	#Вывести информацию об очередях
	pass


    elif '/
    


def main():
    people_at_location = None
    update_id = None
    inf = None
    
    with open('info.conf', 'r') as f:
        inf = json.load(f)
        people_at_location = inf['people_at_location']
        update_id = inf['update_id']
        
    while True:
        resp = getUpdates(update_id)
        print(json.dumps(resp, indent=4))
        if resp['result']:
            for message in resp['result']:
                #text = 'Ты написал мне ' + message['message']['text'].strip().lower()
                answer = answerMessage(message, inf)
                sendMessage(message['message']['chat']['id'], answer)
            
            update_id = resp['result'][-1]['update_id'] + 1

            with open('info.conf', 'w') as f:
                inf['update_id'] = update_id
                json.dump(inf, f, indent=4)         
                
        else:
            pass

        time.sleep(2)
        


if __name__ == '__main__':
    #print(getMe())
    main()
