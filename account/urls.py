<<<<<<< HEAD
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'account'

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard')
]
=======
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'account'

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard_stats')
]
>>>>>>> 3d29c33 (New feature TODOLIST added)
