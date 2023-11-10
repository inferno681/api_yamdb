from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    genre = CharFilter(field_name='genre__slug', method='filter_genre')
    category = CharFilter(
        field_name='category__slug',
        method='filter_category',
    )

    def filter_genre(self, queryset, name, value):
        return queryset.filter(genre__slug=value)

    def filter_category(self, queryset, name, value):
        return queryset.filter(category__slug=value)

    class Meta:
        model = Title
        fields = ['name', 'year']
