import django_filters

from organizations.models import Organization


class OrganizationFilter(django_filters.FilterSet):
    source = django_filters.ChoiceFilter(choices=[("MY", "MY"), ("ALL", "ALL")], method="filter_source")

    def filter_source(self, queryset, _, value):
        if value == "MY":
            return queryset.filter(users=self.request.user)
        else:
            return queryset

    class Meta:
        model = Organization
        fields = ["source"]
