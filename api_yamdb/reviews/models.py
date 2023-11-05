from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'
ROLE_CHOICE = [
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
    (USER, USER)
]
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
INVALID_USERNAME = 'Имя пользователя содержит недопустимые символы.'
INVALID_USERNAME_ME = 'Нельзя использовать имя пользователя "me"'


class User(AbstractUser):

    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=INVALID_USERNAME,
                code='invalid username'
            ),
            RegexValidator(
                regex='me',
                message=INVALID_USERNAME_ME,
                code='invalid username',
                inverse_match=True
            )]
    )
    email = models.EmailField(
        db_index=True,
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    bio = models.TextField(blank=True,)
    role = models.CharField(
        max_length=15,
        default=USER,
        choices=ROLE_CHOICE
    )
    confirmation_code = models.CharField(
        max_length=255,
        blank=True
    )
    last_login = models.DateTimeField(auto_now_add=True)

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    def __str__(self):
        return self.username


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:30]


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:30]


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    rating = models.FloatField()
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre)
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
    score = models.SmallIntegerField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

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

    def __str__(self):
        return self.text[:30]
