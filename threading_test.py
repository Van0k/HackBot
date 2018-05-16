import requests

BACKEND_URL = 'http://52.233.153.23/api'

def apply_for_event(event_id, token):
    r = requests.get(BACKEND_URL + '/events?filter=open', headers={"Authorization": token, "Content-Type": 'application/json'})
    print(r.status_code)
    print(r.text)

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwicm9sZSI6ImhhY2tlciIsImlhdCI6MTUyNjQ5MjE4MiwiZXhwIjoxNTMxNjc2MTgyfQ.cFvsu3CYK4Uo_jU42lCWcqE43FpPbUzOxdUofRJFRZI"
apply_for_event('', TOKEN)


