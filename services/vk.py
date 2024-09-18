from typing import Optional, Tuple

from django.conf import settings
from vk_api import VkApi

from services.utils import get_key_from_link

vk_group_api = VkApi(token=settings.VK_GROUP_TOKEN).get_api()


def _chat_id_to_peer_id(chat_id: int) -> int:
    return 2000000000 + chat_id


def get_vk_user_id(link: str | int) -> Optional[int]:
    if link is None:
        return None

    response = vk_group_api.users.get(user_ids=get_key_from_link(link))
    return response[0]["id"]


def create_vk_chat(title: str) -> Tuple[int, str]:
    chat_id = vk_group_api.messages.createChat(title=title)
    link = vk_group_api.messages.getInviteLink(peer_id=_chat_id_to_peer_id(chat_id))["link"]
    return chat_id, link


def set_vk_admin_role(chat_id: int, member_id: int) -> bool:
    for profile in vk_group_api.messages.getConversationMembers(peer_id=_chat_id_to_peer_id(chat_id))["profiles"]:
        if member_id == profile["id"]:
            vk_group_api.messages.setMemberRole(role="admin", member_id=member_id, peer_id=_chat_id_to_peer_id(chat_id))
            return True
    return False


def send_vk_message(chat_ids: list[int], message: str):
    for chat_id in chat_ids:
        vk_group_api.messages.send(peer_id=_chat_id_to_peer_id(chat_id), message=message, random_id=0)
