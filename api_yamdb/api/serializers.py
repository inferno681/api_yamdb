from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
    FIELDS_LENGTH_LIMITS,
)

from .validators import validate_username, validate_year

EMAIL_OCCUPIED_MESSAGE = 'Пользователь с таким email уже существует'
USERNAME_OCCUPIED_MESSAGE = 'Пользователь с таким username уже существует'
SECOND_REVIEW_PROHIBITION_MESSAGE = {
    'review': ['Вы уже оставляли ревью для этого произведения']}


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleOutputSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        model = Title

    def get_rating(self, obj):
        return get_object_or_404(
            Title,
            pk=obj.id,
        ).reviews.all().aggregate(Avg('score')).get('score__avg')


class TitleInputSerializer(TitleOutputSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
    )
    year = serializers.IntegerField(validators=(validate_year,))

    def to_representation(self, title):
        return TitleOutputSerializer(title).data


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'PATCH' and get_object_or_404(
            Title,
            pk=request.parser_context.get('kwargs').get('title_id'),
        ).reviews.filter(author=request.user).exists():
            raise serializers.ValidationError(
                SECOND_REVIEW_PROHIBITION_MESSAGE)
        return data

    def validate_score(self, score):
        if 0 > score >= 10:
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return score


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=FIELDS_LENGTH_LIMITS['user']['email'], required=True)
    username = serializers.CharField(
        max_length=FIELDS_LENGTH_LIMITS['user']['username'],
        required=True,
        validators=(validate_username,),
    )


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=FIELDS_LENGTH_LIMITS['user']['username'],
        required=True, validators=(validate_username,))
    confirmation_code = serializers.CharField(
        max_length=FIELDS_LENGTH_LIMITS['user']['confirmation_code'],
        required=True)


class UserSerializer(serializers.ModelSerializer):

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

    def validate_username(self, username):
        validate_username(username)
        return username
