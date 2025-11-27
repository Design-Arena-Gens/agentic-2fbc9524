from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('materials/', views.study_materials_view, name='study_materials'),
    path('materials/upload/', views.upload_material_view, name='upload_material'),
    path('groups/', views.study_groups_view, name='study_groups'),
    path('groups/create/', views.create_group_view, name='create_group'),
    path('groups/<int:pk>/', views.group_detail_view, name='group_detail'),
    path('groups/<int:pk>/join/', views.join_group_view, name='join_group'),
    path('requests/<int:pk>/approve/', views.approve_request_view, name='approve_request'),
    path('requests/<int:pk>/reject/', views.reject_request_view, name='reject_request'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_user'),
    path('who-uploaded/', views.who_uploaded_view, name='who_uploaded'),
]
