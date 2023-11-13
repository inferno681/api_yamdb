from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year

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
CONTENT = (
    'Название: {title:.15}. '
    'Текст: {text:.15}. '
    'Автор: {author:.15}. '
    'Дата публикации: {pub_date:.15}. '
)
COMMENT = ('{content_str}'
           'Комментарий: {comment:.15}')
REVIEW = ('{content_str}'
          'Оценка: {score:.15}')
GENRETITLE = ('Жанр: {genre:.15}. '
              'Произведение: {title:.15}. ')
MIN_SCORE = 1
MAX_SCORE = 10
LENGTH_LIMITS_USER_FIELDS = 150
LENGTH_LIMITS_USER_EMAIL = 254
LENGTH_LIMITS_USER_ROLE = max(len(role) for _, role in ROLE_CHOICE)
LENGTH_LIMITS_OBJECT_NAME = 256
LENGTH_LIMITS_OBJECT_SLUG = 50

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
        max_length=LENGTH_LIMITS_USER_FIELDS,
        unique=True,
    )
    email = models.EmailField(
        db_index=True,
        max_length=LENGTH_LIMITS_USER_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        max_length=LENGTH_LIMITS_USER_FIELDS,
        blank=True,
    )
    last_name = models.CharField(
        max_length=LENGTH_LIMITS_USER_FIELDS,
        blank=True,
    )
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=LENGTH_LIMITS_USER_ROLE,
        default=USER,
        choices=ROLE_CHOICE,
    )
    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        blank=True,
        null=True,
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('username',)
        verbose_name = MODELS_LOCALISATIONS['user'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['user'][1]


class GenreCategoryAbstractModel(models.Model):
    """Абстрактная модель для жанров и категорий."""

    name = models.CharField(
        max_length=LENGTH_LIMITS_OBJECT_NAME)
    slug = models.SlugField(
        max_length=LENGTH_LIMITS_OBJECT_SLUG,
        unique=True,
    )

    def __str__(self):
        return self.name[:30]

    class Meta:
        abstract = True
        ordering = ('name',)


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
        max_length=LENGTH_LIMITS_OBJECT_NAME)
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


class ContentAbstractModel(models.Model):
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

    def __str__(self):
        return CONTENT.format(
            title=self.title,
            text=self.text,
            author=self.author,
            pub_date=self.pub_date,
        )


class Review(ContentAbstractModel):
    """Модель отзывов."""

    score = models.SmallIntegerField(
        validators=(
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE),
        ),
    )

    class Meta(ContentAbstractModel.Meta):
        verbose_name = MODELS_LOCALISATIONS['review'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['review'][1]
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique reveview'
            ),
        )

    def __str__(self):
        return REVIEW.format(
            content_str=super().__str__(),
            score=self.score,
        )


class Comment(ContentAbstractModel):
    """Модель комментариев."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')

    class Meta(ContentAbstractModel.Meta):
        verbose_name = MODELS_LOCALISATIONS['comment'][0]
        verbose_name_plural = MODELS_LOCALISATIONS['comment'][1]

    def __str__(self):
        return COMMENT.format(
            content_str=super().__str__(),
            comment=self.text[:30])


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return GENRETITLE.format(
            genre=self.genre,
            title=self.title
        )
