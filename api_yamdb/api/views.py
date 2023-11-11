import random
import string
from statistics import mean

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .permissions import (
    IsAdminOnly,
    IsAdminOrReadOnly,
    IsAuthorOrStuffOrReadOnly,
)
from reviews.models import Category, Genre, Review, Title, User
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    UserSerializer,
)

SENDER = 'admin@ya_mdb.ru'
SUBJECT = 'Код подтверждения'
MESSAGE = ('Привет {username}! \n'
           'Код для получения токена: {confirmation_code}')
NEW_MESSAGE = ('Привет {username}! \n'
               'Новый код для получения токена: {confirmation_code}')
SECOND_REVIEW_PROHIBITION_MESSAGE = {
    'review': ['You are already review this title.']}
USERNAME_OR_EMAIL_OCCUPIED_MESSAGE = 'Такой логин или email уже существуют'
USERNAME_DOESNOT_EXIST_MESSAGE = {'username': 'Пользователь не найден!'}
INVALID_CONFIRMATION_CODE_MESSAGE = {
    'confirmation_code': 'Неверный код подтверждения!'}
LOOKUP_FIELD = 'slug'


class CategotyViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = LOOKUP_FIELD


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = LOOKUP_FIELD


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStuffOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)
        title.rating = self.get_queryset().aggregate(Avg('score')).get(
            'score__avg')
        title.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStuffOrReadOnly)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=self.get_title(),
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title(),
            review=self.get_review(),
        )


class SignUpView(APIView):
    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(**serializer.validated_data)
        user.confirmation_code = '0'
        user.save()
        send_mail(subject=SUBJECT,
                  message=MESSAGE.format(
                      username=user.username,
                      confirmation_code=user.confirmation_code
                  ),
                  from_email=SENDER,
                  recipient_list=(user.email,)
                  )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=request.data['username'])
        if request.data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(
            INVALID_CONFIRMATION_CODE_MESSAGE,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(methods=('GET', 'PATCH'),
            detail=False,
            url_path='me',
            permission_classes=(IsAuthenticated,))
    def get_current_user(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
