import threading
import requests
import time

DELAY = 10

def periodic(interval, action, actionargs=()):
    t =threading.Timer(interval, periodic,
                      (interval, action, actionargs))
    t.start()
    action(*actionargs)

def get_messages_to_send(endpoint):
    r = requests.get(endpoint + '?lastMessageTimestamp=%d&eventId=2' % int(time.time()))
    print(r.text)
    resp = r.json()
    messages = resp
    print(messages)
    return messages

def send_messages(messages, config, bot):
    currentMessageCount = 0
    for message in messages['messages']:
        for receiver in messages['receivers']:
            chat_id = config['users'][str(receiver)]['chat_id']
            bot.send_message(chat_id=chat_id, text=message['content'])
            currentMessageCount += 1
            if currentMessageCount > 10:
                time.sleep(1)
                currentMessageCount = 0
    message_numbers = [message['id'] for message in messages['messages']]
    config['latest_msg'] = max(message_numbers)

def get_and_send_messages(endpoint, config, bot):
    messages = get_messages_to_send(endpoint)
    send_messages(messages, config, bot)

def launch_listener(endpoint, config, bot):
    periodic(DELAY, get_and_send_messages, [endpoint, config, bot])

