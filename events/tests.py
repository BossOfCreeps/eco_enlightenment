from unittest import skip
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from freezegun import freeze_time
from parameterized import parameterized
from rest_framework import status

from events.models import AssistanceOffer, Event, Ticket
from test_utils import _APITestCase
from users.models import User


class EventTests(_APITestCase):
    @parameterized.expand(
        [
            ({}, [1, 2, 3, 4, 5, 6]),
            ({"limit": 2}, [1, 2]),
            ({"offset": 2}, [3, 4, 5, 6]),
            ({"limit": 2, "offset": 2}, [3, 4]),
            ({"date": "2024-01-01"}, [1, 2, 3, 4, 5]),
            ({"date": "2024-01-04"}, [4, 5]),
            ({"q": "b"}, [2, 4, 5]),
            ({"q": "bc"}, [4, 5]),
            ({"q": "abc"}, [4]),
            ({"q": "уникальный"}, [6]),
            ({"q": "уникальная дружбы"}, [6]),
            ({"q": "уникальная дружбы грусть"}, []),
            ({"tags": [1]}, [1, 2, 3, 5]),
            ({"tags": [2]}, [4, 5]),
            ({"tags": [1, 2]}, [5]),
            ({"organization": [1]}, [1, 3, 4, 5, 6]),
            ({"organization": [2]}, [2]),
            ({"organization": [1, 2]}, [1, 2, 3, 4, 5, 6]),
        ]
    )
    def test_list(self, query, result):
        response = self.client.get(reverse("events:events-list"), query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([r["id"] for r in response.json()["results"]], result)

    def test_detail(self):
        response = self.client.get(reverse("events:events-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "name": "a",
                "description": "description",
                "start_date": "2024-01-01T00:00:00+03:00",
                "finish_date": "2024-01-01T00:00:00+03:00",
                "image": None,
                "address": "address",
                "latitude": 1.0,
                "longitude": 1.0,
                "vk_chat_id": 123,
                "vk_chat_link": "http://test.ru",
                "organization": {
                    "id": 1,
                    "users": [
                        {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                        {
                            "email": "email@test.ru",
                            "full_name": None,
                            "vk_link": "https://vk.com/bossofcreeps",
                            "image": None,
                        },
                    ],
                    "full_name": "Полное название",
                    "short_name": "Короткое название",
                    "address": "Адрес",
                    "ogrn": "ОГРН",
                    "inn": "ИНН",
                    "kpp": "КПП",
                    "okpo": "ОКПО",
                    "director_full_name": "Дир ФИО",
                    "director_inn": "Дир ИНН",
                    "activities": "Активности",
                    "reg_date": "2020-01-01",
                    "phone": "Телефон",
                    "email": "Email",
                    "description": "Описание",
                    "image": "/media/foo1.jpg",
                },
                "tags": [{"id": 1, "name": "name"}],
            },
        )

    @patch("services.vk.vk_group_api")
    def test_create(self, mock_vk):
        self.client.force_login(User.objects.get(email="email@test.ru"))

        mock_vk.messages.createChat.return_value = 123
        mock_vk.messages.getInviteLink.return_value = {"link": "http://test.ru"}

        response = self.client.post(
            reverse("events:events-list"),
            {
                "name": "name",
                "address": "address",
                "start_date": "2024-01-01",
                "finish_date": "2024-01-01",
                "description": "description",
                "organization": 1,
                "latitude": 1,
                "longitude": 1,
                "tags": "1,2",
                "image": SimpleUploadedFile("foo_4.jpg", b"1", "image/jpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "id": 7,
                "name": "name",
                "description": "description",
                "start_date": "2024-01-01T00:00:00+03:00",
                "finish_date": "2024-01-01T00:00:00+03:00",
                "image": "http://testserver/media/foo_4.jpg",
                "address": "address",
                "latitude": 1.0,
                "longitude": 1.0,
                "vk_chat_id": 123,
                "vk_chat_link": "http://test.ru",
                "organization": {
                    "id": 1,
                    "users": [
                        {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                        {
                            "email": "email@test.ru",
                            "full_name": None,
                            "vk_link": "https://vk.com/bossofcreeps",
                            "image": None,
                        },
                    ],
                    "full_name": "Полное название",
                    "short_name": "Короткое название",
                    "address": "Адрес",
                    "ogrn": "ОГРН",
                    "inn": "ИНН",
                    "kpp": "КПП",
                    "okpo": "ОКПО",
                    "director_full_name": "Дир ФИО",
                    "director_inn": "Дир ИНН",
                    "activities": "Активности",
                    "reg_date": "2020-01-01",
                    "phone": "Телефон",
                    "email": "Email",
                    "description": "Описание",
                    "image": "/media/foo1.jpg",
                },
                "tags": [{"id": 1, "name": "name"}, {"id": 2, "name": "second"}],
            },
        )

    def test_create_403_organization(self):
        self.client.force_login(User.objects.get(email="email@test.ru"))

        response = self.client.post(
            reverse("events:events-list"),
            {
                "name": "name",
                "address": "address",
                "start_date": "2024-01-01",
                "finish_date": "2024-01-01",
                "description": "description",
                "organization": 2,
                "latitude": 1,
                "longitude": 1,
                "tags": "1,2",
                "image": SimpleUploadedFile("foo_4.jpg", b"1", "image/jpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @skip
    def test_update(self):
        response = self.client.patch(reverse("events:events-detail", args=[1]), {"name": "new"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "name": "new",
                "start_date": "2024-01-01T00:00:00+03:00",
                "finish_date": "2024-01-01T00:00:00+03:00",
                "description": "description",
                "image": None,
                "address": "address",
                "latitude": 1.0,
                "longitude": 1.0,
                "vk_chat_id": 123,
                "vk_chat_link": "http://test.ru",
                "organization": {
                    "id": 1,
                    "users": [
                        {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                        {
                            "email": "email@test.ru",
                            "full_name": None,
                            "vk_link": "https://vk.com/bossofcreeps",
                            "image": None,
                        },
                    ],
                    "full_name": "Полное название",
                    "short_name": "Короткое название",
                    "address": "Адрес",
                    "phone": "Телефон",
                    "email": "Email",
                    "vk": "ВК",
                    "description": "Описание",
                    "type": "NON_COMMERCIAL",
                    "image": "/media/foo1.jpg",
                },
                "tags": [{"id": 1, "name": "name"}],
            },
        )

    @skip
    def test_delete(self):
        response = self.client.delete(reverse("events:events-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 4)

    @parameterized.expand(
        [
            (
                {"link": "https://dobro.ru/event/10661878", "site": "DOBRO_RU"},
                {
                    "name": "Создание статей в новой интернет-энциклопедии РУВИКИ",
                    "description": "<p><span>Новая интернет-энциклопедия РУВИКИ ищет своих авторов! Помощь волонтёров "
                    "понадобится в написании статей и внесении правок в уже существующие материалы. Вы "
                    "можете писать статьи <b>на любую тему,</b> которая отзывается у вас в душе, "
                    "или выбрать <b>из списка</b> приведенного ниже.</span></p><ul><li>Комиксы: "
                    "MARVEL, DC, Bubble (персонажи, издательства, художники, "
                    "сюжетные ветки)</li><li>Манга</li><li>Юношеский спорт</li><li>Краеведческие "
                    "музеи&nbsp;</li><li>Киберспорт (турниры, спортсмены, команды, "
                    "игры)</li><li>Статьи на языках народов России</li><li>Известные личности, "
                    "культура, история народов России</li><li>Сериалы, "
                    "актеры сериалов</li><li>Современные писатели и издательства</li><li>Музыка ("
                    "исполнители, альбомы, студии)</li><li>Любая тема, которая вам "
                    "нравится.</li></ul><p><b>Требования к статьям:</b></p><ul><li>Статьи на эту тему "
                    "не должно существовать в РУВИКИ.</li><li>Статья должна быть написана нейтральным "
                    "языком.</li><li>Статья должна быть оригинальной или переведенной с любого "
                    "языка.</li><li>Рекомендованный размер статьи 500 слов, так как он легче всего "
                    "воспринимается читателями.</li><li>Все тезисы статьи должны быть подкреплены "
                    "авторитетными источниками.</li></ul><p>После одобрения вашей заявки, на указанный "
                    "вами имейл придет письмо, <b>содержащие все необходимые инструкции и способы "
                    "связи с командой</b> на случай, если у вас появятся вопросы. Мы обязательно "
                    "проведем вас за руку через все коды и шаблоны РУВИКИ, потому что знаем, "
                    "что это бывает непросто!</p><p>С <b>базовыми правилами</b> написания статей вы "
                    "можете ознакомиться здесь: https://meta.ruwiki.ru/wiki/Краткие_правила.</p><p>Как "
                    "только статья будет готова, присылайте ссылку на нее на имейл authors@ruwiki.ru, "
                    "мы убедимся, что она соответствует требованиям и начислим вам "
                    "часы.</p><p><b>Базовое количество часов, которые получает каждый участник: 5 (за "
                    "минимальное количество слов).&nbsp;</b></p><p>Количество часов зависит "
                    "от:</p><p>1. Количества слов в статье (300), (300-600), (600-900) (900+) "
                    "</p><p>2. Количества источников&nbsp;</p>",
                    "start_date": "2024-03-22T14:00:00+03:00",
                    "end_date": "2024-12-31T22:00:00+03:00",
                    "location": "Онлайн",
                    "image": "https://storage.yandexcloud.net/dobro-static/prod/images/46823f09-0cae-bdc4-786a"
                    "-89fe6c7b4718.png",
                },
            ),
            (
                {"link": "https://leader-id.ru/events/514459/", "site": "LEADER_ID"},
                {
                    "name": "Роль молодёжи в современной политике",
                    "description": "Встреча за круглым столом на тему «Роль молодежи в современной политике», "
                    "которая пройдет 6 сентября 2024 года в Точке кипения-Томск, станет важным "
                    "событием для молодых людей, интересующихся политикой и общественной "
                    "деятельностью. Время проведения – с 15:00 до 17:00, адрес мероприятия – Проспект "
                    "Ленина, 26. Главной целью этого мероприятия является оказание поддержки учащейся "
                    "молодежи в профориентации и развитии ключевых навыков для участия в "
                    "общественно-политической жизни.<br><br>Это мероприятие предназначено для "
                    "школьников и студентов, которые желают понять, как они могут существенно влиять "
                    "на социальную и политическую жизнь своего региона и страны в целом. Также "
                    "приглашены ребята и эксперты из различных муниципальных образований, "
                    "которые смогут присоединиться через видеоконференцсвязь. Это позволит создать "
                    "более широкую дискуссионную платформу и включить в обсуждение как можно больше "
                    "заинтересованных лиц.<br><br>В рамках круглого стола планируется участие видных "
                    "общественных и политических деятелей Томской области, которые смогут поделиться "
                    "своим опытом и знаниями с молодежью. Участники мероприятия получат уникальную "
                    "возможность задать вопросы экспертам и узнать из первых уст о карьерных путях в "
                    "политике, необходимых шагах и навыках для успешной работы в данной сфере. Это "
                    "создаст для них реальную перспективу понимания и определения собственного "
                    "профессионального пути.<br><br>Польза данного мероприятия очевидна и многогранна. "
                    "Во-первых, оно будет способствовать образованию и карьерному развитию молодых "
                    "людей, помогая им осознать свои возможности и пути реализации в политике и "
                    "общественной деятельности. Во-вторых, личное общение с успешными фигурами может "
                    "послужить мощным источником вдохновения и мотивации для каждого участника. "
                    "В-третьих, полученные знания и рекомендации помогут создавать и развивать "
                    "необходимые для политического и общественного участия компетенции. В-четвертых, "
                    "мероприятие предоставит отличную возможность для нетворкинга, что может стать "
                    "основой для будущих совместных проектов и инициатив между молодыми активистами и "
                    "экспертами.<br><br>Мы уверены, что вовлечение молодежи в политические процессы "
                    "важно для стабильного и успешного будущего нашего общества. Присоединяйтесь к "
                    "нам, чтобы вместе строить лучшее будущее! Для регистрации на мероприятие, "
                    "пожалуйста, воспользуйтесь ссылкой, которая будет предоставлена после "
                    "бронирования. По всем вопросам обращайтесь к Томскому региональному отделению "
                    "«Российский союз сельской молодежи» – мы рады помочь сделать ваше участие "
                    "комфортным и продуктивным.",
                    "start_date": "2024-09-06T15:00:00",
                    "end_date": "2024-09-06T18:00:00",
                    "location": "Точка кипения - Томск",
                    "image": "https://leader-id.storage.yandexcloud.net/upload/6159960/69a73497-820b-4ff2-876e"
                    "-d5ec84578ef0.png",
                },
            ),
            (
                {"link": "https://afisha.timepad.ru/event/3020375", "site": "TIMEPAD"},
                {
                    "name": "Дискуссия «Книга с четырёх сторон» /// ТОМ II",
                    "description": "<p>Вы берёте в руки книгу — прямоугольный объект, у которого есть разные стороны. "
                    "Обложка, книжный блок, корешок, обрез… Но и в метафорическом плане любое издание "
                    "имеет разные стороны — ведь в его создании принимают участие многие люди, "
                    "профессионально занимаясь частями того, что станет единым целым. Издатель "
                    "выбирает текст, художник придаёт книге определённый облик, редактор превращает её "
                    "в то, чем, собственно, и является книга — во внятный и грамотный текст. А потом "
                    "появляется читатель или его уполномоченный представитель — библиотекарь, "
                    "— и книга становится явлением культуры. У каждого из участников этого "
                    "захватывающего процесса своя роль, особая ответственность и немало занимательных "
                    "историй из практики. Дискуссия, открывающая фестиваль, будет посвящена тому, "
                    "как благодаря воле и умению специалистов создаётся такое удивительное явление, "
                    "как книга.</p><br><br><p>В дискуссии примут "
                    "участие:</p><br><br><ul><br>\t<li>главный редактор издательства «Макушин "
                    "Медиа»\xa0<strong>Елена Фаткулина</strong>,</li><br>\t<li>художник-иллюстратор "
                    "<strong>Игорь Олейников</strong>,</li><br>\t<li>редактор книг по искусству, "
                    "заведующая редакционно-издательским отделом ГМИИ им. А.С. Пушкина <strong>Ксения "
                    "Велиховская</strong>,</li><br>\t<li>директор Научной библиотеки ТГУ <strong>Артём "
                    "Васильев</strong>.</li><br></ul><br><br><p>Модератор: искусствовед, "
                    "советник директора ГМИИ им. А.С. Пушкина\xa0<strong>Анна Гор</strong>.</p><br>",
                    "start_date": "2024-09-12T17:00:00+03:00",
                    "end_date": "2024-09-12T18:30:00+03:00",
                    "location": "Колонный зал Центра культуры ТГУ,\r\nпроспект Ленина, д. 36,\r\nЦентр культуры ТГУ, "
                    "3 этаж",
                    "image": "https://ucare.timepad.ru/51a9821c-1f28-4dae-ad17-2d0770454fcf/-/preview/308x600/-/format"
                    "/jpeg/poster_event_3020375.jpg",
                },
            ),
        ]
    )
    def test_parse_site(self, query, result):
        response = self.client.get(reverse("events:events-parsesite"), query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), result)

    def test_make_ics(self):
        response = self.client.get(reverse("events:events-makeics", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.content,
            b"BEGIN:VCALENDAR\r\n"
            b"VERSION:2.0\r\n"
            b"PRODID:ics.py - http://git.io/lLljaA\r\n"
            b"BEGIN:VEVENT\r\n"
            b"DESCRIPTION:description\r\n"
            b"DTEND:20231231T210000Z\r\n"
            b"LOCATION:address\r\n"
            b"DTSTART:20231231T210000Z\r\n"
            b"SUMMARY:a\r\n"
            b"UID:00000000-0000-0000-0000-000000000001\r\n"
            b"END:VEVENT\r\n"
            b"END:VCALENDAR",
        )

    @patch("services.vk.vk_group_api")
    def test_make_admin_in_vk_chat(self, mock_vk):
        self.client.force_login(User.objects.get(email="2@test.ru"))

        response = self.client.post(reverse("events:events-makeadmininvkchat", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"message": "Пользователь не установил ВК"})

        User.objects.filter(email="2@test.ru").update(vk_id=1)

        response = self.client.post(reverse("events:events-makeadmininvkchat", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"message": "Пользователь не находится в чате"})

        mock_vk.messages.getConversationMembers.return_value = {"profiles": [{"id": 1}]}

        response = self.client.post(reverse("events:events-makeadmininvkchat", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_make_admin_in_vk_chat_403(self):
        self.client.force_login(User.objects.get(email="email@test.ru"))

        response = self.client.post(reverse("events:events-makeadmininvkchat", args=[2]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parse_description(self):
        self.assertEqual(
            sorted(Event.objects.get(id=6).extra["search"]),
            [
                "20",
                "33",
                "7000",
                "бол",
                "взаимоуважен",
                "вид",
                "включа",
                "волонтер",
                "всемирн",
                "высок",
                "выступлен",
                "город",
                "движен",
                "двух",
                "деятельн",
                "диалог",
                "дружб",
                "игр",
                "идеал",
                "котор",
                "летн",
                "международн",
                "межкультурн",
                "мультиспортивн",
                "направлен",
                "объект",
                "окажут",
                "организац",
                "основ",
                "открыт",
                "перв",
                "планир",
                "поддержк",
                "привлеч",
                "принцип",
                "проведен",
                "пространств",
                "себ",
                "событ",
                "соревнован",
                "спорт",
                "станет",
                "уникальн",
                "функциональн",
                "эгид",
            ],
        )


class EventTagTests(_APITestCase):
    def test_list(self):
        response = self.client.get(reverse("events:tags-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{"id": 1, "name": "name"}, {"id": 2, "name": "second"}])

    def test_detail(self):
        response = self.client.get(reverse("events:tags-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"id": 1, "name": "name"})


class TicketTests(_APITestCase):
    @parameterized.expand(
        [
            ({}, [(1, 1, "email@test.ru"), (2, 2, "email@test.ru")]),
            ({"event": 1}, [(1, 1, "email@test.ru")]),
            ({"user": "email@test.ru"}, [(1, 1, "email@test.ru"), (2, 2, "email@test.ru")]),
        ]
    )
    def test_list(self, query, result):
        response = self.client.get(reverse("events:tickets-list"), query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([(r["id"], r["event"]["id"], r["user"]["email"]) for r in response.json()], result)

    def test_detail(self):
        response = self.client.get(reverse("events:tickets-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "user": {
                    "email": "email@test.ru",
                    "full_name": None,
                    "vk_link": "https://vk.com/bossofcreeps",
                    "image": None,
                },
                "created_at": "2024-09-16T03:00:00+03:00",
                "event": {
                    "id": 1,
                    "name": "a",
                    "description": "description",
                    "start_date": "2024-01-01T00:00:00+03:00",
                    "finish_date": "2024-01-01T00:00:00+03:00",
                    "image": None,
                    "address": "address",
                    "latitude": 1.0,
                    "longitude": 1.0,
                    "vk_chat_id": 123,
                    "vk_chat_link": "http://test.ru",
                    "organization": {
                        "id": 1,
                        "users": [
                            {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                            {
                                "email": "email@test.ru",
                                "full_name": None,
                                "vk_link": "https://vk.com/bossofcreeps",
                                "image": None,
                            },
                        ],
                        "full_name": "Полное название",
                        "short_name": "Короткое название",
                        "address": "Адрес",
                        "ogrn": "ОГРН",
                        "inn": "ИНН",
                        "kpp": "КПП",
                        "okpo": "ОКПО",
                        "director_full_name": "Дир ФИО",
                        "director_inn": "Дир ИНН",
                        "activities": "Активности",
                        "reg_date": "2020-01-01",
                        "phone": "Телефон",
                        "email": "Email",
                        "description": "Описание",
                        "image": "/media/foo1.jpg",
                    },
                    "tags": [{"id": 1, "name": "name"}],
                },
            },
        )

    @freeze_time("2017-06-23 07:28:00")
    def test_create(self):
        self.client.force_login(User.objects.get(email="email@test.ru"))

        response = self.client.post(reverse("events:tickets-list"), {"event": 5})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "id": 3,
                "user": {
                    "email": "email@test.ru",
                    "full_name": None,
                    "vk_link": "https://vk.com/bossofcreeps",
                    "image": None,
                },
                "created_at": "2017-06-23T10:28:00+03:00",
                "event": {
                    "id": 5,
                    "name": "bc",
                    "description": "description",
                    "start_date": "2024-01-01T00:00:00+03:00",
                    "finish_date": "2024-01-05T00:00:00+03:00",
                    "image": None,
                    "address": "address",
                    "latitude": 1.0,
                    "longitude": 1.0,
                    "vk_chat_id": 123,
                    "vk_chat_link": "http://test.ru",
                    "organization": {
                        "id": 1,
                        "users": [
                            {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                            {
                                "email": "email@test.ru",
                                "full_name": None,
                                "vk_link": "https://vk.com/bossofcreeps",
                                "image": None,
                            },
                        ],
                        "full_name": "Полное название",
                        "short_name": "Короткое название",
                        "address": "Адрес",
                        "ogrn": "ОГРН",
                        "inn": "ИНН",
                        "kpp": "КПП",
                        "okpo": "ОКПО",
                        "director_full_name": "Дир ФИО",
                        "director_inn": "Дир ИНН",
                        "activities": "Активности",
                        "reg_date": "2020-01-01",
                        "phone": "Телефон",
                        "email": "Email",
                        "description": "Описание",
                        "image": "/media/foo1.jpg",
                    },
                    "tags": [{"id": 1, "name": "name"}, {"id": 2, "name": "second"}],
                },
            },
        )

    @skip
    def test_delete(self):
        response = self.client.delete(reverse("events:tickets-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ticket.objects.count(), 1)


class AssistanceOfferTests(_APITestCase):
    @parameterized.expand(
        [({}, [(1, 1, 1), (2, 2, 1)]), ({"event": 2}, [(2, 2, 1)]), ({"organization": 1}, [(1, 1, 1), (2, 2, 1)])]
    )
    def test_list(self, query, result):
        response = self.client.get(reverse("events:assistance_offers-list"), query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([(r["id"], r["event"]["id"], r["organization"]["id"]) for r in response.json()], result)

    def test_detail(self):
        response = self.client.get(reverse("events:assistance_offers-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "text": "text",
                "created_at": "2024-09-16T03:00:00+03:00",
                "event": {
                    "id": 1,
                    "name": "a",
                    "description": "description",
                    "start_date": "2024-01-01T00:00:00+03:00",
                    "finish_date": "2024-01-01T00:00:00+03:00",
                    "image": None,
                    "address": "address",
                    "latitude": 1.0,
                    "longitude": 1.0,
                    "vk_chat_id": 123,
                    "vk_chat_link": "http://test.ru",
                    "organization": {
                        "id": 1,
                        "users": [
                            {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                            {
                                "email": "email@test.ru",
                                "full_name": None,
                                "vk_link": "https://vk.com/bossofcreeps",
                                "image": None,
                            },
                        ],
                        "full_name": "Полное название",
                        "short_name": "Короткое название",
                        "address": "Адрес",
                        "ogrn": "ОГРН",
                        "inn": "ИНН",
                        "kpp": "КПП",
                        "okpo": "ОКПО",
                        "director_full_name": "Дир ФИО",
                        "director_inn": "Дир ИНН",
                        "activities": "Активности",
                        "reg_date": "2020-01-01",
                        "phone": "Телефон",
                        "email": "Email",
                        "description": "Описание",
                        "image": "/media/foo1.jpg",
                    },
                    "tags": [{"id": 1, "name": "name"}],
                },
                "organization": {
                    "id": 1,
                    "users": [
                        {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                        {
                            "email": "email@test.ru",
                            "full_name": None,
                            "vk_link": "https://vk.com/bossofcreeps",
                            "image": None,
                        },
                    ],
                    "full_name": "Полное название",
                    "short_name": "Короткое название",
                    "address": "Адрес",
                    "ogrn": "ОГРН",
                    "inn": "ИНН",
                    "kpp": "КПП",
                    "okpo": "ОКПО",
                    "director_full_name": "Дир ФИО",
                    "director_inn": "Дир ИНН",
                    "activities": "Активности",
                    "reg_date": "2020-01-01",
                    "phone": "Телефон",
                    "email": "Email",
                    "description": "Описание",
                    "image": "/media/foo1.jpg",
                },
            },
        )

    @freeze_time("2017-06-23 07:28:00")
    def test_create(self):
        response = self.client.post(
            reverse("events:assistance_offers-list"), {"event": 5, "organization": 2, "text": "qwer"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "id": 3,
                "text": "qwer",
                "created_at": "2017-06-23T10:28:00+03:00",
                "event": {
                    "id": 5,
                    "name": "bc",
                    "description": "description",
                    "start_date": "2024-01-01T00:00:00+03:00",
                    "finish_date": "2024-01-05T00:00:00+03:00",
                    "image": None,
                    "address": "address",
                    "latitude": 1.0,
                    "longitude": 1.0,
                    "vk_chat_id": 123,
                    "vk_chat_link": "http://test.ru",
                    "organization": {
                        "id": 1,
                        "users": [
                            {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                            {
                                "email": "email@test.ru",
                                "full_name": None,
                                "vk_link": "https://vk.com/bossofcreeps",
                                "image": None,
                            },
                        ],
                        "full_name": "Полное название",
                        "short_name": "Короткое название",
                        "address": "Адрес",
                        "ogrn": "ОГРН",
                        "inn": "ИНН",
                        "kpp": "КПП",
                        "okpo": "ОКПО",
                        "director_full_name": "Дир ФИО",
                        "director_inn": "Дир ИНН",
                        "activities": "Активности",
                        "reg_date": "2020-01-01",
                        "phone": "Телефон",
                        "email": "Email",
                        "description": "Описание",
                        "image": "/media/foo1.jpg",
                    },
                    "tags": [{"id": 1, "name": "name"}, {"id": 2, "name": "second"}],
                },
                "organization": {
                    "id": 2,
                    "users": [
                        {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                        {
                            "email": "3@test.ru",
                            "full_name": None,
                            "vk_link": "https://vk.com/bossofcreeps",
                            "image": None,
                        },
                    ],
                    "full_name": "Полное название",
                    "short_name": "Короткое название",
                    "address": "Адрес",
                    "ogrn": "ОГРН",
                    "inn": "ИНН",
                    "kpp": "КПП",
                    "okpo": "ОКПО",
                    "director_full_name": "Дир ФИО",
                    "director_inn": "Дир ИНН",
                    "activities": "Активности",
                    "reg_date": "2020-01-01",
                    "phone": "Телефон",
                    "email": "Email",
                    "description": "Описание",
                    "image": "/media/foo2.jpg",
                },
            },
        )

    @skip
    def test_delete(self):
        response = self.client.delete(reverse("events:assistance_offers-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AssistanceOffer.objects.count(), 1)
