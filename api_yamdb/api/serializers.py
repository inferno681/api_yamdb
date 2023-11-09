from datetime import date
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User)

INVALID_USERNAME = 'Имя пользователя содержит недопустимые символы.'
INVALID_USERNAME_ME = 'Нельзя использовать имя пользователя "me"'
EMAIL_OCCUPIED = {'email': 'Пользователь с таким email уже существует'}
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
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
    )
    description = serializers.CharField(required=False)

    class Meta:
        fields = '__all__'
        model = Title
        read_only_fields = ('rating',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        title = Title.objects.get(id=data['id'])
        data['category'] = {
            'name': title.category.name,
            'slug': title.category.slug
        }
        data['genre'] = [
            {
                'name': genre.name,
                'slug': genre.slug,
            } for genre in title.genre.all()
        ]
        return data

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(genre_id=genre, title_id=title)
        return title

    def validate_year(self, value):
        year = date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        exclude = ('title',)
        model = Review
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        exclude = ('title', 'review')
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
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=255, required=True)

    class Meta:
        fields = ('username', 'confirmation_code')
        model = User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True, validators=(
        UniqueValidator(message=EMAIL_OCCUPIED, queryset=User.objects.all()),))
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
            ),
            UniqueValidator(
                message=USERNAME_OCCUPIED,
                queryset=User.objects.all()
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
