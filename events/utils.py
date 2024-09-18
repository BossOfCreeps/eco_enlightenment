from events.models import Event
from services import send_email, send_vk_message


def mass_send_new_event(event: Event):
    # TODO:
    #  надо будет в будущем завести celery задачу, но в рамках прототипа делаем синхронно
    #  доработать логику на тэги

    # мероприятие от того же организатора
    message = (
        "Приветствую!\n"
        "\n"
        f'{event.organization.full_name} приглашает Вас принять участие в нашем мероприятии "{event.name}".\n'
        f'Оно состоится {event.start_date.strftime("%d.%m.%Y %H:%M")}, по адресу {event.address}.\n'
        f"Подробности можно узнать по ссылке: {event.get_absolute_url()}\n"
        f"\n"
        "До встречи!"
    )

    vk_chat_ids, user_emails = set(), set()
    for event in Event.objects.prefetch_related("tickets").filter(organization=event.organization):
        vk_chat_ids.add(event.vk_chat_id)
        for ticket in event.tickets.all():
            user_emails.add(ticket.user.email)

    send_email(f'Новое мероприятие от {event.organization.short_name}: "{event.name}"', message, list(user_emails))
    send_vk_message(list(vk_chat_ids), message)
