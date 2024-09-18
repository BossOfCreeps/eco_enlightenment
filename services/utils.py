def get_key_from_link(link: str | int, *, letter: str = "/") -> str | int:
    """
    Примеры:

    https://leader-id.ru/events/514459/
    https://dobro.ru/event/10661878
    https://afisha.timepad.ru/event/3020375

    """
    if type(link) is int or link.isdigit():
        return link

    return link.rstrip("/").split(letter)[-1]
