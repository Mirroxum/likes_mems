from django.contrib.auth import get_user_model
from django.db import models

from likes_mems.conf import MAX_LEN_MEM_NAME

User = get_user_model()

class Mem(models.Model):
    name = models.CharField(
        verbose_name='Название мема',
        max_length=MAX_LEN_MEM_NAME,
        unique=True
    )
    image = models.ImageField(
        verbose_name='Изображение мема',
        upload_to='recipes/images',
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
    likes = models.IntegerField(
        default=0,
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Мем'
        verbose_name_plural = 'Мемы'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}. Лайки: {self.likes}'