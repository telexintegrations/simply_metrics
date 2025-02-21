import requests

url = "https://ping.telex.im/v1/webhooks/01952a22-7f63-7d0b-813c-1cc46ef09e5a"
payload = {
    "event_name": "string",
    "message": "python post",
    "status": "success",
    "username": "collins"
}

response = requests.post(
    url,
    json=payload,
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
)
print(response.json())