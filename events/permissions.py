from rest_framework.permissions import SAFE_METHODS, BasePermission

from events.models import Event


class EventPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False

        if view.action == "create":
            if not request.user.organizations.filter(pk=request.data["organization"]).exists():
                return False

        return True

    def has_object_permission(self, request, view, obj: Event):
        if view.action == "make_admin_in_vk_chat":
            if not request.user.organizations.filter(pk=obj.organization_id).exists():
                return False

        return True
