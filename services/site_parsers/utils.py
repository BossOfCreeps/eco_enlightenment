from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class SiteParseEnum(Enum):
    DOBRO_RU = "DOBRO_RU"
    LEADER_ID = "LEADER_ID"
    TIMEPAD = "TIMEPAD"
    VK_WALL = "VK_WALL"
    VK_EVENT = "VK_EVENT"


@dataclass
class EventParserTemplate:
    name: Optional[str]
    description: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    location: Optional[str]
    image: Optional[str]
