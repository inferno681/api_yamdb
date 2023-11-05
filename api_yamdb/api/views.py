from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins, viewsets, permissions
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)

from reviews.models import Category, Comment, Genre, Review, Title
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer
)


class CategotyViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_object(self):
        category_slug = self.kwargs.get('pk')
        category = get_object_or_404(Category, slug=category_slug)
        return category


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_object(self):
        genre_slug = self.kwargs.get('pk')
        genre = get_object_or_404(Genre, slug=genre_slug)
        return genre


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(rating=0)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        queryset = self.get_title().reviews.all()
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review

    def get_queryset(self):
        queryset = self.get_review().comments.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_review())
