
from django.contrib import admin
from django.urls import path

from app.views import (
    index,
    login, logout,
    register,
    profile,
    change_password, forget_password,
    reset_password,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', index, name='index'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('change_password/', change_password, name='change_password'),
    path('forget_password/', forget_password, name='forget_password'),

    path(
        'reset_password/<uidb64>/<token>/',
        reset_password,
        name = 'reset_password',
    ),
]
