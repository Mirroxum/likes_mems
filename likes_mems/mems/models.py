from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

from likes_mems.conf import (MAX_LEN_MEM_NAME,
                             MAX_LEN_COMMUNITY_NAME,
                             MAX_LEN_COMMUNITY_DESCRIPTION,
                             MAX_LEN_USERNAME,
                             MAX_LEN_EMAIL,
                             MAX_LEN_LAST_AND_FIRST_NAME)


class User(AbstractUser):
    ROLES_CHOICES = [
        ('user', 'user'),
        ('premiumuser', 'premiumuser'),
    ]

    username = models.CharField(
        'Username', max_length=MAX_LEN_USERNAME, unique=True
    )
    first_name = models.CharField(
        'Firstname', max_length=MAX_LEN_LAST_AND_FIRST_NAME
    )
    last_name = models.CharField(
        'Lastname', max_length=MAX_LEN_LAST_AND_FIRST_NAME
    )
    email = models.EmailField(
        'Email',
        max_length=MAX_LEN_EMAIL,
        help_text='Укажи свой e-mail.',
        unique=True,
    )
    role = models.CharField(
        'Roles', choices=ROLES_CHOICES, default='user', max_length=14
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}'

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_premium(self):
        return self.role == 'premiumuser'


class Mem(models.Model):
    name = models.CharField(
        verbose_name='Название мема',
        max_length=MAX_LEN_MEM_NAME,
        unique=True
    )
    image = models.ImageField(
        verbose_name='Изображение мема',
        upload_to='images/',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='mems',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    is_favorite = models.BooleanField(
        default=False,
        verbose_name='Продвижение мема',
    )

    class Meta:
        verbose_name = 'Мем'
        verbose_name_plural = 'Мемы'
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.name}. Автор:{self.author.username}.'


class LikeDislikeManager(models.Manager):
    use_for_related_fields = True

    def likes(self):
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        return self.get_queryset().filter(vote__lt=0)

    def sum_rating(self):
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0


class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTES = (
        (DISLIKE, 'Не нравится'),
        (LIKE, 'Нравится')
    )
    vote = models.SmallIntegerField(
        verbose_name=("Голос"),
        choices=VOTES)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=("Пользователь")
    )
    mem = models.ForeignKey(
        Mem,
        on_delete=models.CASCADE,
        related_name='likesdislikes',
        verbose_name=("Мем")
    )
    objects = LikeDislikeManager()

    class Meta:
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоса'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'mem', ),
                name='unique_for_user_mem'
            ),
        )

    def __str__(self):
        return (f'Пользователь:{self.user.username} '
                f'поставил {self.vote} на '
                f'мем:{self.mem}')


class Сommunity(models.Model):
    name = models.CharField(
        verbose_name='Название сообщества',
        max_length=MAX_LEN_COMMUNITY_NAME,
        unique=True
    )
    description = models.CharField(
        verbose_name='Описание сообщества',
        max_length=MAX_LEN_COMMUNITY_DESCRIPTION,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Slug сообщества',
        max_length=MAX_LEN_COMMUNITY_NAME,
        unique=True
    )
    users = models.ManyToManyField(
        User,
        related_name='community',
        blank=True
    )
    mems = models.ManyToManyField(
        Mem,
        related_name='community',
        blank=True
    )

    class Meta:
        verbose_name = 'Мемное сообщество'
        verbose_name_plural = 'Мемные сообщества'

    def __str__(self):
        return self.name
