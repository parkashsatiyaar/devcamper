from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('register', views.register, name='register'),
    path('verify', views.verify, name='verify'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('deactivate', views.deactivate, name='deactivate'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('reset_verify', views.reset_verify, name='reset_verify'),
]
