from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('', include('users.urls')),
    # path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # path('api/token/', TokenObtainPairView.as_view()),
    # path('api/token/refresh/',TokenRefreshView.as_view()),
]
if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
