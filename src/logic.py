import requests

def get_sessions():
    url = "https://ujian.pages.dev/sessions.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None
