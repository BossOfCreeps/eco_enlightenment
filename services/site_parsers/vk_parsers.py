from datetime import datetime

from django.conf import settings
from vk_api import VkApi

from services.site_parsers.utils import EventParserTemplate
from services.utils import get_key_from_link

vk_app_api = VkApi(token=settings.VK_APP_TOKEN).get_api()


def parse_vk_wall(link: str) -> EventParserTemplate:
    event_data = vk_app_api.wall.getById(posts=get_key_from_link(link, letter="wall"))[0]

    image = None
    for attachment in event_data["attachments"]:
        if attachment["type"] == "photo":
            max_w, link = 0, None
            for size in attachment["photo"]["sizes"]:
                if size["width"] > max_w:
                    max_w = size["width"]
                    image = size["url"]

    return EventParserTemplate(
        name=None,
        description=event_data["text"],
        start_date=None,
        end_date=None,
        location=None,
        image=image,
    )


def parse_vk_event(link: str) -> EventParserTemplate:
    event_data = vk_app_api.groups.getById(
        group_id=get_key_from_link(link), fields="description,start_date,finish_date,addresses"
    )[0]
    return EventParserTemplate(
        name=event_data["name"],
        description=event_data["description"],
        start_date=datetime.fromtimestamp(event_data["start_date"]),
        end_date=datetime.fromtimestamp(event_data["finish_date"]),
        location=event_data["addresses"].get("main_address", {}).get("additional_address"),
        image=event_data["photo_200"],
    )
