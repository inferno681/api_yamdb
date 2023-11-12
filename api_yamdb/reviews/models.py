from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import validate_year

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'
ROLE_CHOICE = (
    (ADMIN, "Админ"),
    (MODERATOR, "Модератор"),
    (USER, "Пользователь")
)
TITLE = (
    'Название: {name:.15}. '
    'Год: {year:.15}. '
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
SCORE_VALUES = {
    'min_value': 1,
    'max_value': 10,
}
FIELDS_LENGTH_LIMITS = {
    'user': {
        'username': 150,
        'email': 254,
        'first_name': 150,
        'last_name': 150,
        'role': max(len(role) for _, role in ROLE_CHOICE),
        'confirmation_code': 6,
    },
    'genre_category': {
        'name': 256,
        'slug': 50,
    },
    'title': {
        'name': 256,
    }
}

MODELS_LOCALISATIONS = {
    'user': ('Пользователь', 'Пользователи'),
    'genre': ('Жанр', 'Жанры'),
    'category': ('Категория', 'Категории'),
    'title': ('Произведение', 'Произведения'),
    'review': ('Обзор', 'Обзоры'),
    'comment': ('Комментарий', 'Комментарии'),
}


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        db_index=True,
        max_length=FIELDS_LENGTH_LIMITS['user']['username'],
        unique=True,
    )
    email = models.EmailField(
        db_index=True,
        max_length=FIELDS_LENGTH_LIMITS['user']['email'],
        unique=True,
    )
    first_name = models.CharField(
        max_length=FIELDS_LENGTH_LIMITS['user']['first_name'],
        blank=True,
    )
    last_name = models.CharField(
        max_length=FIELDS_LENGTH_LIMITS['user']['last_name'],
        blank=True,
    )
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=FIELDS_LENGTH_LIMITS['user']['role'],
        default=USER,
        choices=ROLE_CHOICE,
    )
    confirmation_code = models.CharField(
        max_length=FIELDS_LENGTH_LIMITS['user']['confirmation_code'],
        blank=True,
        null=True
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = MODELS_LOCALISATIONS['user'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['user'][1]


class GenreCategoryAbstractModel(models.Model):
    """Абстрактная модель для жанров и категорий."""

    name = models.CharField(
        max_length=FIELDS_LENGTH_LIMITS['genre_category']['name'])
    slug = models.SlugField(
        max_length=FIELDS_LENGTH_LIMITS['genre_category']['slug'],
        unique=True,
    )

    def __str__(self):
        return self.name[:30]

    class Meta:
        abstract = True
        ordering = ('slug',)


class Genre(GenreCategoryAbstractModel):
    """Модель жанров."""

    class Meta(GenreCategoryAbstractModel.Meta):
        verbose_name = MODELS_LOCALISATIONS['genre'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['genre'][1]


class Category(GenreCategoryAbstractModel):
    """Модель категорий."""

    class Meta(GenreCategoryAbstractModel.Meta):
        verbose_name = MODELS_LOCALISATIONS['category'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['category'][1]


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(
        max_length=FIELDS_LENGTH_LIMITS['title']['name'])
    year = models.IntegerField(validators=(validate_year,))
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
    )

    def __str__(self):
        return TITLE.format(
            name=self.name,
            year=self.year,
            description=self.description,
            genre=self.genre,
            category=self.category
        )

    class Meta:
        ordering = ('-year', 'name')
        verbose_name = MODELS_LOCALISATIONS['title'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['title'][1]


class ReviewTitleAbstractModel(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='%(class)ss')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='%(class)ss')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(ReviewTitleAbstractModel):
    """Модель отзывов."""

    score = models.SmallIntegerField(
        validators=(
            MinValueValidator(SCORE_VALUES['min_value']),
            MaxValueValidator(SCORE_VALUES['max_value']),
        ),
    )

    class Meta(ReviewTitleAbstractModel.Meta):
        verbose_name = MODELS_LOCALISATIONS['review'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['review'][1]
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique reveview'
            ),
        )

    def __str__(self):
        return REVIEW.format(
            title=self.title,
            text=self.text,
            author=self.author,
            score=self.score,
            pub_date=self.pub_date,
        )


class Comment(ReviewTitleAbstractModel):
    """Модель комментариев."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')

    class Meta(ReviewTitleAbstractModel.Meta):
        verbose_name = MODELS_LOCALISATIONS['comment'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['comment'][1]

    def __str__(self):
        return self.text[:30]


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'
