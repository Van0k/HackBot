import requests
import hashlib
import hmac
import json

BACKEND_URL = 'http://52.233.153.23/api'


def user_login(data, hash):
    data['hash'] = hash
    r = requests.post(BACKEND_URL + '/login/telegram', json=data)
    print(r.text)
    resp = r.json()
    print(resp)
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
    print(r.text)

    resp = json.loads(r.text)
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
        print(r.text)
        print(r.status_code)
        raise ValueError


def get_participants(event_id, token):
    r = requests.get(BACKEND_URL + '/admin/participants/%s' % event_id, headers={"Authorization": token, "Content-Type": 'application/json'})
    return r.json()

def participation_status_activate(token, event_id, password, location):
    password = password if password else 'null'
    print(location)
    if location:
        request_data = {"enteringWord": password, "location": {'lat': location['latitude'], 'lng': location['longitude']}}
    else:
        request_data = {"enteringWord": password}

    r = requests.post(BACKEND_URL + '/events/%s/activate' % event_id,
                      data=json.dumps(request_data),
                      headers={"Authorization": token, "Content-Type": 'application/json'})
    print(r.text)
    resp = r.json()
    return resp['status']


def participation_status_finish(event_id, token):
    r = requests.post(BACKEND_URL + '/events/%s/finish' % event_id,
                      data=json.dumps({}),
                      headers={"Authorization": token, "Content-Type": 'application/json'})
    print(r.text)
    resp = r.json()
    return resp['status']

def participation_status_revert(event_id, token):
    r = requests.post(BACKEND_URL + '/events/%s/activate' % event_id,
                      data=json.dumps({}),
                      headers={"Authorization": token, "Content-Type": 'application/json'})
    print(r.text)
    resp = r.json()
    return resp['status']

def toggle_searchable(event_id, token):
    r = requests.post(BACKEND_URL + '/events/%s/toggle_is_searchable' % event_id,
                      data=json.dumps({}),
                      headers={"Authorization": token, "Content-Type": 'application/json'})
    print(r.text)
    resp = r.json()
    return resp['isSearchable']

def get_event(event_id, token):
    r = requests.get(BACKEND_URL + '/events/%s' % event_id,
                     headers={"Authorization": token, "Content-Type": 'application/json'})

    print(r.text)
    resp = r.json()
    return resp

def get_participant_admin(event_id, participant_id, token):
    r = requests.get(BACKEND_URL + '/admin/participants/%s' % event_id, headers={"Authorization": token, "Content-Type": 'application/json'})
    participants = r.json()
    chosen_participant = [p for p in participants if p['id'] == participant_id][0]

    return chosen_participant
