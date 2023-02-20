from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Mem, LikeDislike


class LikeDislikeInline(admin.TabularInline):
    model = LikeDislike
    extra = 1


@admin.register(Mem)
class MemAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_image', 'author',
                    'pub_date', 'sum_rating', 'likes',
                    'dislikes', 'is_favorite')
    inlines = [LikeDislikeInline, ]

    def sum_rating(self, obj):
        return obj.likesdislikes.sum_rating()

    def likes(self, obj):
        return obj.likesdislikes.likes().count()

    def dislikes(self, obj):
        return obj.likesdislikes.dislikes().count()

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" height="110"')

    get_image.short_description = 'Изображение'


@admin.register(LikeDislike)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'mem', 'vote')
