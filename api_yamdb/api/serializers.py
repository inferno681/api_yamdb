from rest_framework import serializers, relations
from rest_framework.relations import SlugRelatedField

from reviews.models import (Category, Comment, Genre, Review, Title, User,
                            GenreTitle)


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('__all__')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleListSerializer(serializers.ListSerializer):
    child = serializers.DictField(
        child=serializers.CharField()
    )


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
