import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from services.site_parsers.utils import EventParserTemplate
from services.utils import get_key_from_link


def parse_dobro_ru(link: str) -> EventParserTemplate:
    soup = BeautifulSoup(requests.get(f"https://dobro.ru/event/{get_key_from_link(link)}").content)
    full_data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
    event_data = full_data["props"]["pageProps"]["initialState"]["eventReducer"]["event"]

    return EventParserTemplate(
        name=event_data["name"],
        description=event_data["description"],
        start_date=datetime.fromisoformat(event_data["eventPeriod"]["startDate"]),
        end_date=datetime.fromisoformat(event_data["eventPeriod"]["endDate"]),
        location=event_data["location"]["title"],
        image=event_data["imageFile"]["url"],
    )
