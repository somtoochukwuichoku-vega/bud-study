from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),

    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='roomUrl'),

    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.UpdateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.DeleteRoom, name='delete-room'),

]
