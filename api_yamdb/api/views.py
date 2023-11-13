import random

from django.core.mail import send_mail
from django.db.models import Avg, Q
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
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from .filters import TitleFilter
from .permissions import (
    IsAdminOnly,
    IsAdminOrReadOnly,
    IsAuthorOrStuffOrReadOnly,
)
from reviews.models import Category, Genre, Review, Title, User
from django.conf import settings
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleOutputSerializer,
    TitleInputSerializer,
    UserSerializer,
)
import query_debugger


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

EMAIL_OCCUPIED_MESSAGE = 'Пользователь с таким email уже существует'
USERNAME_OCCUPIED_MESSAGE = 'Пользователь с таким username уже существует'


class CategoryGenreMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = LOOKUP_FIELD
    filter_backends = (filters.SearchFilter,)


class CategotyViewSet(CategoryGenreMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')).order_by('-year', 'name')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleOutputSerializer
        return TitleInputSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStuffOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


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
        queryset = User.objects.filter(
            Q(username=request.data['username']) | Q(
                email=request.data['email'])
        )
        if len(queryset) == 2:
            raise ValidationError({
                'username': [USERNAME_OCCUPIED_MESSAGE],
                'email': [EMAIL_OCCUPIED_MESSAGE],
            })
        user = queryset.first()
        if user and user.username != request.data['username']:
            raise ValidationError(
                {'email': [EMAIL_OCCUPIED_MESSAGE]})
        if user and user.email != request.data['email']:
            raise ValidationError(
                {'username': [USERNAME_OCCUPIED_MESSAGE]})
        user, created = User.objects.get_or_create(**serializer.validated_data)
        user.confirmation_code = '0'
        # .join(random.choices(
        #     settings.CONFIRMATION_CODE_SYMBOLS,
        #     k=settings.CONFIRMATION_CODE_LENGTH),
        # )
        user.save()
        send_mail(subject=SUBJECT,
                  message=MESSAGE.format(
                      username=user.username,
                      confirmation_code=user.confirmation_code
                  ),
                  from_email=settings.ADMIN_EMAIL,
                  recipient_list=(user.email,)
                  )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=serializer.data['username'])
        if request.data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            user.confirmation_code = None
            user.save()
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
            return Response(UserSerializer(request.user).data)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
