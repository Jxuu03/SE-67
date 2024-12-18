from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('reset-password/', resetPassword, name='reset-password'),
    path('', home, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
