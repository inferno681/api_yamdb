import re
from rest_framework import serializers, relations
from rest_framework.relations import SlugRelatedField
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.models import (
    Category, Comment, Genre, Review, Title, User, GenreTitle)


INVALID_USERNAME = 'Имя пользователя содержит недопустимые символы.'
INVALID_USERNAME_ME = 'Нельзя использовать имя пользователя "me"'
INVALID_USERNAME_EMAIL = 'Такой пользователь уже существует'
EMAIL_OCCUPIED = 'Пользователь с таким email уже существует'
USERNAME_OCCUPIED = 'Пользователь с таким username уже существует'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(many=True,
                                         queryset=Genre.objects.all(),
                                         slug_field='slug'
                                         )
    description = serializers.CharField(required=False)

    class Meta:
        fields = '__all__'
        model = Title
        read_only_fields = ('rating',)

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre = Genre.objects.get(slug=genre)
            GenreTitle.objects.create(
                genre=current_genre, title=title)
            title.genre.add(current_genre)
        return title


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('__all__')
        model = Review
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('title', 'review')


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=INVALID_USERNAME,
                code='invalid username'
            ),
            RegexValidator(
                regex=r'^me$',
                message=INVALID_USERNAME_ME,
                code='invalid username',
                inverse_match=True
            )
        )
    )

    class Meta:
        fields = ('email', 'username')
        model = User


class GetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'confirmation_code')
        model = User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=INVALID_USERNAME,
                code='invalid username'
            ),
            RegexValidator(
                regex=r'^me$',
                message=INVALID_USERNAME_ME,
                code='invalid username',
                inverse_match=True
            )
        )
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User
        read_only = ('role',)

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].user.is_admin:
            fields['role'].read_only = False
        return fields
