import requests


def otp_send(recipient, otp):
    url = 'https://console.melipayamak.com/api/send/shared/ab7e45a6a3cf48d7b60939dbcae698ce'
    body = {
        "bodyId": 53822,
        "to": recipient,
        "args": [recipient, otp]
    }

    x = requests.post(url, json=body)
    return x.json()
