import requests
import os

url = "https://eventor.orientering.se/api/results/event"
apikey = os.environ["apikey"]
headers = {'ApiKey': apikey}

response = requests.get(url, headers=headers, params={'eventId': 23906, 'includeSplitTimes': False})

print(response)