import requests
import os
import urllib3


urllib3.disable_warnings()
directory = 'books'
path_to_package = os.getcwd()
os.makedirs(os.path.join(path_to_package, directory), exist_ok=True)
url = 'https://tululu.org/txt.php'
headers = {'User-Agent': 'user_agent', }
for book_id in range(1, 11):
    payload = {'id': book_id}
    response = requests.get(url=url, headers=headers, params=payload, verify=False)
    response.raise_for_status()
    if response.headers['Content-Type'] == 'text/plain; charset="utf-8"':
        with open(f'{directory}\\id{book_id}.txt', 'w', encoding='utf8') as file:
            file.write(response.text)
