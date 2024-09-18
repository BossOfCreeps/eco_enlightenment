import json
from datetime import datetime

import requests
from django.conf import settings

from services.site_parsers.utils import EventParserTemplate
from services.utils import get_key_from_link


def parse_leader_id(link: str) -> EventParserTemplate:
    access_token = requests.post(
        "https://apps.leader-id.ru/api/v1/oauth/token",
        json={
            "client_id": settings.LEADER_ID_CLIENT_ID,
            "client_secret": settings.LEADER_ID_CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
    ).json()["access_token"]

    event_data = requests.get(
        f"https://apps.leader-id.ru/api/v1/events?ids[]={get_key_from_link(link)}",
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()["items"][0]

    return EventParserTemplate(
        name=event_data["name"],
        description="".join([block["data"]["text"] for block in json.loads(event_data["info"])["blocks"]]),
        start_date=datetime.fromisoformat(event_data["dateStart"]),
        end_date=datetime.fromisoformat(event_data["dateEnd"]),
        location=event_data["space"][0]["name"],
        image=event_data["photo"]["full"],
    )
