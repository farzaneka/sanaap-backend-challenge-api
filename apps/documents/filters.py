import django_filters

from apps.documents.models import Document


class DocumentFilter(django_filters.FilterSet):
    """Supported query params:

    - ?title=<icontains>
    - ?content_type=<exact>
    - ?owner=<user id>
    - ?tags=<icontains>
    - ?created_after=<date>
    - ?created_before=<date>
    """

    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    tags = django_filters.CharFilter(field_name="tags", lookup_expr="icontains")
    content_type = django_filters.CharFilter(field_name="content_type", lookup_expr="iexact")
    owner = django_filters.NumberFilter(field_name="owner_id")
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Document
        fields = ["title", "tags", "content_type", "owner", "created_after", "created_before"]
