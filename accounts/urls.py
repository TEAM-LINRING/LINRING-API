"""
URL configuration for teatalk_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account.views import ConfirmEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from accounts.views import UserDetailsViewOverride, PasswordChangeView, UserViewSet, get_refresh_view, \
    UserLogoutViewOverride, TagSetViewSet

router = routers.DefaultRouter()
router.register(r'tagset', TagSetViewSet)
router.register(r'user', UserViewSet)
urlpatterns = [
    path('token/refresh/', get_refresh_view().as_view()),

    path('', include('dj_rest_auth.urls')),
    re_path(r'^register/account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
            name='account_confirm_email'),
    path('register/', include('dj_rest_auth.registration.urls')),
    path('password/reset/confirm/<str:uidb64>/<str:token>', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('api-token-auth/', obtain_auth_token),
    path('v2/', include([
        path('', include(router.urls)),
        path('user/me/', UserDetailsViewOverride.as_view(), name='rest_user_details'),
        path('user/detail/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'})),
        path('password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
        path('logout/', UserLogoutViewOverride.as_view(), name='rest_logout'),


    ]))
]
