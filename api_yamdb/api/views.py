from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from reviews.models import Category, Comment, Genre, Review, Title, User
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer
)


SENDER = 'admin@ya_mdb.ru'
SUBJECT = 'Код подтверждения'
MESSAGE = ('Привет {username}! \n'
           'Код для получения токена: {confirmation_code}')


class CategotyViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_review())


class SignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SignUpSerializer

    def perform_create(self, serializer):
        serializer.save()
        username = self.request.data['username']
        user = User.objects.get(username=username)
        User.objects.filter(username=username).update(
            confirmation_code=default_token_generator.make_token(user))
        user.refresh_from_db()
        send_mail(subject=SUBJECT,
                  message=MESSAGE.format(
                      username=user.username,
                      confirmation_code=user.confirmation_code
                  ),
                  from_email=SENDER,
                  recipient_list=[user.email,]
                  )
