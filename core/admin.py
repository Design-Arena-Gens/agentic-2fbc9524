from django.contrib import admin
from .models import UserProfile, StudyMaterial, StudyGroup, GroupJoinRequest

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'bio']
    search_fields = ['user__username']

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploader', 'upload_date', 'views']
    list_filter = ['upload_date']
    search_fields = ['title', 'uploader__username']

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'creator__username']

@admin.register(GroupJoinRequest)
class GroupJoinRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'group__name']
