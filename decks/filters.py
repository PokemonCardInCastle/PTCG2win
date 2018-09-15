from django_filters import filters
from django_filters import FilterSet


class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = "%s (降順)"


class DeckFilter(FilterSet):

    name = filters.CharFilter(name='name', label='名前', lookup_expr='contains')
    description = filters.CharFilter(name='description', label='説明', lookup_expr='contains')
    arch_type = filters.CharFilter(name='arch_type', label='デッキタイプ', lookup_expr='contains')

    order_by = MyOrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('name', 'name'),
            ('arch_type', 'arch_type'),
        ),
        field_labels={
            'name': '氏名',
            'arch_type': 'デッキタイプ',
        },
        label='並び順'
    )




