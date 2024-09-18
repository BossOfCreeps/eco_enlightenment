from datetime import datetime

import requests
from django.conf import settings

from services.site_parsers.utils import EventParserTemplate
from services.utils import get_key_from_link


def parse_timepad(link: str) -> EventParserTemplate:
    event_data = requests.get(
        f"https://api.timepad.ru/v1/events/{get_key_from_link(link)}",
        headers={"Authorization": f"Bearer {settings.TIMEPAD_TOKEN}"},
    ).json()

    return EventParserTemplate(
        name=event_data["name"],
        description=event_data["description_html"].replace("\n", "<br>"),
        start_date=datetime.fromisoformat(event_data["starts_at"]),
        end_date=datetime.fromisoformat(event_data["ends_at"]),
        location=event_data["location"]["address"],
        image=event_data["poster_image"]["default_url"],
    )
