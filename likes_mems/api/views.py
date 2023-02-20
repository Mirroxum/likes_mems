from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.http import HttpResponseRedirect
from django.db.models import Sum, F
from rest_framework.pagination import PageNumberPagination

from mems.models import Mem, LikeDislike, Сommunity
from .serializers import MemSerializer, СommunitySerializer, UserSerializer
from utils.random_chance import is_promote
from likes_mems.conf import CHANCE


User = get_user_model()


class MemViewSet(APIView):

    def get(self, request):
        to_mem = Mem.objects.annotate(sum_votes=Sum(
            F('likesdislikes__vote'))).order_by('sum_votes', '?').first()
        return HttpResponseRedirect(
            redirect_to=reverse('memdetail', kwargs={'pk': to_mem.pk}))


class MemDetailViewSet(APIView):

    def get(self, request, pk):
        mem = get_object_or_404(Mem, pk=pk)
        serializer = MemSerializer(mem)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK)


class MemSkipViewSet(APIView):

    def get(self, request, pk):
        current_mem = get_object_or_404(Mem, pk=pk)
        favorite_mems = Mem.objects.filter(is_favorite=True)
        if (is_promote(CHANCE) and not
                current_mem.is_favorite and favorite_mems.exists()):
            to_mem = favorite_mems.order_by('?').first()
        else:
            to_mem = Mem.objects.annotate(sum_votes=Sum(
                F('likesdislikes__vote'))).order_by('sum_votes', '?').first()
        return HttpResponseRedirect(
            redirect_to=reverse('memdetail', kwargs={'pk': to_mem.pk}))


class LikeViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        user = self.request.user
        mem = get_object_or_404(Mem, pk=pk)
        try:
            old_mark = LikeDislike.objects.get(user=user, mem=mem)
            if old_mark.vote == 1:
                return Response({
                    'errors': 'Вы уже лайкали этот мем'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif old_mark.vote == -1:
                old_mark.vote = 1
                old_mark.save()
        except LikeDislike.DoesNotExist:
            LikeDislike.objects.create(user=user, mem=mem, vote=1)
        return HttpResponseRedirect(
            redirect_to=reverse('memskip', kwargs={'pk': pk}))


class DisLikeViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        user = self.request.user
        mem = get_object_or_404(Mem, pk=pk)
        try:
            old_mark = LikeDislike.objects.get(user=user, mem=mem)
            if old_mark.vote == -1:
                return Response({
                    'errors': 'Вы уже дизлайкали этот мем'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif old_mark.vote == 1:
                old_mark.vote = -1
                old_mark.save()
        except LikeDislike.DoesNotExist:
            LikeDislike.objects.create(user=user, mem=mem, vote=-1)
        return HttpResponseRedirect(
            redirect_to=reverse('memskip', kwargs={'pk': pk}))


class CommunityViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = СommunitySerializer
    queryset = Сommunity.objects.all()
    lookup_field = 'slug'
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @action(methods=['get'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def mems(self, request, slug):
        current_community = get_object_or_404(Сommunity, slug=slug)
        mems = Mem.objects.filter(community=current_community)
        pages = self.paginate_queryset(mems)
        serializer = MemSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['get'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def users(self, request, slug):
        current_community = get_object_or_404(Сommunity, slug=slug)
        users = User.objects.filter(community=current_community)
        pages = self.paginate_queryset(users)
        serializer = UserSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, slug=None):
        user = request.user
        through_obj = Сommunity.users.through.objects
        current_community = get_object_or_404(Сommunity, slug=slug)
        is_subscribe = through_obj.filter(
            user_id=user.id, сommunity_id=current_community.id).exists()
        if is_subscribe:
            through_obj.filter(
                user_id=user.id, сommunity_id=current_community.id).delete()
            return Response({'success': 'Вы успешно отписались'
                             }, status=status.HTTP_204_NO_CONTENT)
        else:
            through_obj.create(
                user_id=user.id, сommunity_id=current_community.id)
        return Response({'success': 'Вы уcпешно подписались'
                         }, status=status.HTTP_201_CREATED)
