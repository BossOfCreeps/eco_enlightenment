from pprint import pprint

from django.conf import settings
from gigachat import GigaChat


def gpt_call(payload: str):
    with GigaChat(credentials=settings.GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
        response = giga.chat(payload)
        data = response.choices[0].message.content
        pprint(data)
        return data
