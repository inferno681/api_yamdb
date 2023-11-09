from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.models import (
    Category, Comment, Genre, Review, Title, User, GenreTitle)


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


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

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
    class Meta:
        fields = ('email', 'username')
        model = User


class GetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'confirmation_code')
        model = User
