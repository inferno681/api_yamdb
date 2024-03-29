from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategotyViewSet,
    CommentViewSet,
    GenreViewSet,
    GetTokenView,
    ReviewViewSet,
    SignUpView,
    TitleViewSet,
    UserViewSet,
)

router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'categories', CategotyViewSet, basename='category')
router_v1.register(r'genres', GenreViewSet, basename='genre')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)
router_v1.register(r'users', UserViewSet, basename='users')

signup_urls = [
    path('auth/signup/', SignUpView.as_view(), name='get_token'),
    path('auth/token/', GetTokenView.as_view(), name='signup'),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include(signup_urls)),
]
