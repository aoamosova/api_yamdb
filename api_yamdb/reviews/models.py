from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_year


class User(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Administrator'),
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    role = models.CharField(max_length=256, choices=ROLES, default=ROLES[0][0])
    email = models.EmailField(_('email address'), blank=False, unique=True, max_length=254)
    bio = models.TextField(_('biography'), blank=True,)
    confirmation_code = models.IntegerField(_('confirmation code'), blank=True, null=True)

    def __str__(self):
        return self.username


class Genres(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Categories(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Titles(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    year = models.IntegerField(
        verbose_name='Дата создания',
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genres,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Categories,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name="titles",
        blank=True,
        null=True
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Призведения'
        ordering = ['name']


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Titles,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genres,
        verbose_name='Жанр',
        on_delete=models.CASCADE
    )

    def ___str__(self):
        return f'{self.title}, жанр - {self.genre}'

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Reviews(models.Model):
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
        related_name='reviews'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews'
    )

    def __str__(self) -> str:
        return self.text

    def delete(self, using=None, keep_parents=False):
        rating_obj, created = Ratings.objects.get_or_create(title=self.title)
        rating_obj.count_score = rating_obj.count_score - 1
        rating_obj.summ_score = rating_obj.summ_score - self.score
        if rating_obj.count_score == 0:
            rating_obj.rating = 0
        else:
            rating_obj.rating = rating_obj.summ_score / rating_obj.count_score
        rating_obj.save()
        return super().delete(using, keep_parents)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='uniq_reviews_title_author'
            )
        ]


class Comments(models.Model):
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Комментатор',
        related_name='comments'
    )
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='comments'
    )
    review = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.author}: {self.text}'


class Ratings(models.Model):
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='rating_title'
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        default=1
    )
    count_score = models.IntegerField(
        verbose_name='Количество оценок',
        default=0
    )
    summ_score = models.IntegerField(
        verbose_name='Сумма оценок',
        default=0
    )

    def __str__(self) -> str:
        return f'{self.title.text}: {self.rating}'
