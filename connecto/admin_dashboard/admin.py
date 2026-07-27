from django.contrib import admin
from .models import (
    AdminProfile, Report, VerificationRequest, AdminNotification,
    AdminActivityLog, SiteSettings, UserWarning, UserSuspension,
    UserVerificationStatus, PostModeration
)

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'created_at')
    list_filter = ('role', 'department')
    search_fields = ('user__username', 'user__email', 'department')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'reported_user', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('reporter__username', 'reported_user__username', 'description')

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'reason')

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'target', 'created_at')
    list_filter = ('notification_type', 'target', 'created_at')
    search_fields = ('title', 'message')

@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'target_type', 'target_label', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('admin__username', 'details', 'target_label', 'ip_address')

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_by', 'updated_at')
    search_fields = ('key', 'value', 'description')

@admin.register(UserWarning)
class UserWarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'issued_by', 'severity', 'is_acknowledged', 'created_at')
    list_filter = ('severity', 'is_acknowledged', 'created_at')
    search_fields = ('user__username', 'reason')

@admin.register(UserSuspension)
class UserSuspensionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'issued_by', 'is_active', 'expires_at', 'created_at')
    list_filter = ('action', 'is_active', 'created_at')
    search_fields = ('user__username', 'reason')

@admin.register(UserVerificationStatus)
class UserVerificationStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'verified_by', 'verified_at')
    list_filter = ('is_verified', 'verified_at')
    search_fields = ('user__username',)

@admin.register(PostModeration)
class PostModerationAdmin(admin.ModelAdmin):
    list_display = ('post', 'status', 'moderated_by', 'updated_at')
    list_filter = ('status', 'updated_at')
    search_fields = ('post__caption', 'moderation_reason')
