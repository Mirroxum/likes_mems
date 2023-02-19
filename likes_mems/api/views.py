from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect

from mems.models import Mem, LikeDislike
from .serializers import MemSerializer


User = get_user_model()


class MemViewSet(APIView):

    def get(self, request):
        mem = Mem.objects.select_related('author').first()
        pk = mem.pk
        return HttpResponseRedirect(
            redirect_to=reverse('memdetail', kwargs={'pk': pk}))


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
        current_pub_date = current_mem.pub_date
        to_mem = Mem.objects.filter(pub_date__gt=current_pub_date).first()
        if to_mem:
            return HttpResponseRedirect(
                redirect_to=reverse('memdetail', kwargs={'pk': to_mem.pk}))
        else:
            return HttpResponseRedirect(
                redirect_to=reverse('mem'))


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
