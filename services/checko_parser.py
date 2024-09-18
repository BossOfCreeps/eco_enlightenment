import datetime
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings


@dataclass
class OrganizationParserTemplate:
    full_name: str
    short_name: str
    address: str
    ogrn: str
    inn: str
    kpp: str
    okpo: str
    director_full_name: str
    director_inn: str
    reg_date: datetime.date
    phone: Optional[str]
    email: Optional[str]


def parse_organization_by_inn(inn: str) -> OrganizationParserTemplate:
    # https://checko.ru/user/account/api

    response = requests.get(f"https://api.checko.ru/v2/company?key={settings.CHECKO_API_KEY}&inn={inn}")
    data = response.json()["data"]

    phones = data["Контакты"]["Тел"]
    emails = data["Контакты"]["Емэйл"]

    return OrganizationParserTemplate(
        ogrn=data["ОГРН"],
        inn=data["ИНН"],
        kpp=data["КПП"],
        okpo=data["ОКПО"],
        reg_date=datetime.date.fromisoformat(data["ДатаРег"]),
        short_name=data["НаимСокр"],
        full_name=data["НаимПолн"],
        address=data["ЮрАдрес"]["АдресРФ"],
        director_full_name=data["Руковод"][0]["ФИО"],
        director_inn=data["Руковод"][0]["ИНН"],
        phone=phones[0] if phones else None,
        email=emails[0] if emails else None,
    )
