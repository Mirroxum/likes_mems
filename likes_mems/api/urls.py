from django.urls import include, path
from rest_framework.routers import SimpleRouter
from djoser.views import UserViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (MemViewSet, MemDetailViewSet,
                    MemSkipViewSet, LikeViewSet,
                    DisLikeViewSet, CommunityViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Documentation Mem API",
        default_version='v1',
    ),
    public=True,
)
v1_router = SimpleRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('community', CommunityViewSet, basename='community')
urlpatterns = [
    path('', include(v1_router.urls)),
    path('mem/', MemViewSet.as_view(), name='mem'),
    path('mem/<int:pk>/', MemDetailViewSet.as_view(), name='memdetail'),
    path('mem/<int:pk>/skip', MemSkipViewSet.as_view(), name='memskip'),
    path('mem/<int:pk>/like', LikeViewSet.as_view(), name='like'),
    path('mem/<int:pk>/dislike', DisLikeViewSet.as_view(), name='dislike'),
    path('auth/', include('djoser.urls.authtoken')),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
