from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activate/<str:uid>/<str:token>/', views.activate, name='activate'),
    path('', views.dashboard, name='dashboard')
]