import requests

url = "https://rest.api.eu-central-1.production.jet-external.com/autocomplete/addresses/nl"

params = {
    "input": "Almere",
    "type": "any",
    "session": "YOUR_SESSION_VALUE",
    "limit": 20,
}

response = requests.get(url, params=params)

response.raise_for_status()

data = response.json()

print(data)