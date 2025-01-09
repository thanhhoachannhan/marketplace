
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from app.views import (
    index,
    login, logout,
    register,
    profile,
    change_password, forget_password,
    reset_password,

    api_order_detail,
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

    path(
        'api_order_detail/<int:order_id>/',
        api_order_detail,
        name = 'api_order_detail'
    ),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)