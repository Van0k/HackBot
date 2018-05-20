import threading
import requests
import time
import os

DELAY = 3
MESSAGES_TOKEN = os.environ['MESSAGE_TOKEN'] # Token for message endpoints here

def periodic(interval, action, actionargs=()):
    t = threading.Timer(interval, periodic,
                      (interval, action, actionargs))
    t.start()
    action(*actionargs)

def get_messages_to_send(endpoint):
    r = requests.get(endpoint + '?eventId=1', headers={"Authorization": MESSAGES_TOKEN, "Content-Type": 'application/json'})
    resp = r.json()
    messages = resp
    return messages

def send_messages(messages, config, bot):
    if messages['messages']:
        currentMessageCount = 0
        for message in messages['messages']:
            for receiver in messages['receivers']:
                try:
                    chat_id = config['users'][str(receiver)]['chat_id']
                    bot.send_message(chat_id=chat_id, text=message['content'])
                except:
                    print('Error on sending: {}'.format(receiver))
                currentMessageCount += 1
                if currentMessageCount > 10:
                    time.sleep(1)
                    currentMessageCount = 0
            time.sleep(0.1)

def get_and_send_messages(endpoint, config, bot):
    messages = get_messages_to_send(endpoint)
    send_messages(messages, config, bot)

def launch_listener(endpoint, config, bot):
    periodic(DELAY, get_and_send_messages, [endpoint, config, bot])

