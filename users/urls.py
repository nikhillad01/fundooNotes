from django.urls import path
from . import views
from django.conf.urls import url
from django.contrib.auth import views as auth_views
# from users.views import loginview
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home1, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('index/', views.index, name='index'),

    path('getnotes/<slug:uid>/',views.getnotes.as_view()),
    path('addnote/',views.addnote.as_view()),
    path('updatenote/<int:pk>/',views.updatenote.as_view()),
    path('deletenote/<int:pk>/',views.deletenote.as_view()),

    url(r'^lazy_load_notes/$', views.lazy_load_notes, name='lazy_load_notes'),

     #path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
     #path('login/', views.loginview, name='login'),


     url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
         views.activate, name='activate'),
     path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),

]


urlpatterns = format_suffix_patterns(urlpatterns)
