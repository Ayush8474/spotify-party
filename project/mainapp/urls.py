from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login),
    path('login-success/', views.login_success),
    path('search/', views.search)
    #path('track/', views.track)
]