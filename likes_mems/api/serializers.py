from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from mems.models import User, Mem


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
        )
        read_only_fields = '__all__',


class MemSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Mem
        fields = (
            'id',
            'name',
            'image',
            'author',
            'pub_date',
            'likes',
        )

    def get_likes(self, obj):
        return obj.likesdislikes.sum_rating()
