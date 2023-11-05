from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()
TITLE = (
    'Название: {name:.15}. '
    'Год: {year:.15}. '
    'Рейтинг: {rating:.15}. '
    'Описание: {description:.15}. '
    'Жанр: {genre:.15}. '
    'Категория: {category:.15}. '
)
REVIEW = (
    'Название: {title:.15}. '
    'Текст: {text:.15}. '
    'Автор: {author:.15}. '
    'Оценка: {score:.15}. '
    'Дата публикации: {pub_date:.15}. '
)


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:30]


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:30]


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(max_length=256)
    year = models.IntegerField()
    rating = models.FloatField(
        validators=(MinValueValidator(1), MaxValueValidator(10)),
    )
    description = models.TextField()
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return Title.format(
            name=self.name,
            year=self.year,
            rating=self.rating,
            description=self.description,
            genre=self.genre,
            category=self.category
        )


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.SmallIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(10)),
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return REVIEW.format(
            title=self.title,
            text=self.author,
            score=self.score,
            pub_date=self.pub_date,
        )


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:30]


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'
