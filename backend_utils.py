import requests
import hashlib
import hmac
import json

BACKEND_URL = 'http://52.233.153.23/api'

def user_login(data, hash):
    data['hash'] = hash
    r = requests.post(BACKEND_URL + '/login/telegram', json=data)
    resp = r.json()

    return resp['token']

def get_skills(token):
    r = requests.get(BACKEND_URL + '/skills', headers={"Authorization": token, "Content-Type": 'application/json'})
    resp = r.json()
    return resp

def get_data_hash(data, bot_token):
    bot_token_key = hashlib.sha256(bytes(bot_token, encoding='utf-8')).digest()
    checkString = '\n'.join(['{}={}'.format(key, data[key]) for key in sorted(data.keys())])
    HMAC_string = hmac.new(bot_token_key, msg=bytes(checkString, encoding='utf-8'), digestmod=hashlib.sha256).hexdigest()
    return HMAC_string

def get_current_user(token):
    r = requests.get(BACKEND_URL + '/hackers/me', headers={"Authorization": token, "Content-Type": 'application/json'})
    resp = r.json()
    return resp

def update_current_user(token, data):
    data.pop('id')
    data.pop('tgProfileLink')
    data.pop('stat')
    data_string = json.dumps(data)
    r = requests.put(BACKEND_URL + '/hackers/me', data=data_string, headers={"Authorization": token, "Content-Type": 'application/json'})
    if r.status_code != 200:
        raise ValueError

def apply_for_event(event_id, token):
    r = requests.post(BACKEND_URL + '/events/%s/apply' % event_id, headers={"Authorization": token, "Content-Type": 'application/json'})
    if not r.status_code in [200, 409]:
        raise ValueError
    print(r.status_code)
    print(r.text)

