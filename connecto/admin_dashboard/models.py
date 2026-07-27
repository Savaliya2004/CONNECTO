from django.db import models
from django.contrib.auth.models import User
from myapp.models import InstaUser, InstaPost


class AdminProfile(models.Model):
    """Extended profile for admin users with role-based access."""
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('content_moderator', 'Content Moderator'),
        ('support_staff', 'Support Staff'),
        ('viewer', 'Viewer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='viewer')
    avatar = models.ImageField(upload_to='admin_avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def can_manage_users(self):
        return self.role in ('super_admin', 'admin', 'moderator')

    @property
    def can_delete_content(self):
        return self.role in ('super_admin', 'admin', 'content_moderator', 'moderator')

    @property
    def can_view_analytics(self):
        return self.role in ('super_admin', 'admin', 'moderator', 'viewer')

    @property
    def can_manage_settings(self):
        return self.role in ('super_admin', 'admin')

    @property
    def can_ban_users(self):
        return self.role in ('super_admin', 'admin')

    @property
    def can_send_notifications(self):
        return self.role in ('super_admin', 'admin', 'moderator')

    @property
    def can_approve_verification(self):
        return self.role in ('super_admin', 'admin')


class Report(models.Model):
    """User-submitted reports for content or accounts."""
    REASON_CHOICES = (
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('fake_account', 'Fake Account'),
        ('violence', 'Violence'),
        ('nudity', 'Nudity'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('action_taken', 'Action Taken'),
    )

    reporter = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name='submitted_reports')
    reported_user = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name='received_reports', null=True, blank=True)
    reported_post = models.ForeignKey(InstaPost, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter.username} — {self.get_reason_display()}"


class VerificationRequest(models.Model):
    """Blue badge verification requests."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('more_info', 'More Information Required'),
    )

    user = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name='verification_requests')
    reason = models.TextField()
    document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_verifications')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification request by {self.user.username} — {self.get_status_display()}"


class AdminNotification(models.Model):
    """Admin-sent notifications to users."""
    TYPE_CHOICES = (
        ('system', 'System Notification'),
        ('maintenance', 'Maintenance Notice'),
        ('announcement', 'Announcement'),
        ('warning', 'Warning'),
        ('promotion', 'Promotion'),
    )
    TARGET_CHOICES = (
        ('everyone', 'Everyone'),
        ('verified', 'Verified Users'),
        ('creators', 'Creators'),
        ('selected', 'Selected Users'),
    )

    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_admin_notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default='everyone')
    selected_users = models.ManyToManyField(InstaUser, blank=True, related_name='admin_notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"


class AdminActivityLog(models.Model):
    """Tracks all admin actions for audit trail."""
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('user_edit', 'User Edit'),
        ('user_suspend', 'User Suspend'),
        ('user_ban', 'User Ban'),
        ('user_activate', 'User Activate'),
        ('user_delete', 'User Delete'),
        ('post_delete', 'Post Delete'),
        ('post_hide', 'Post Hide'),
        ('post_feature', 'Post Feature'),
        ('comment_delete', 'Comment Delete'),
        ('report_review', 'Report Review'),
        ('report_dismiss', 'Report Dismiss'),
        ('verification_approve', 'Verification Approve'),
        ('verification_reject', 'Verification Reject'),
        ('notification_sent', 'Notification Sent'),
        ('settings_change', 'Settings Change'),
        ('password_reset', 'Password Reset'),
        ('other', 'Other'),
    )

    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50, blank=True, null=True)  # 'user', 'post', etc.
    target_id = models.IntegerField(null=True, blank=True)
    target_label = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        admin_name = self.admin.username if self.admin else 'System'
        return f"{admin_name} — {self.get_action_display()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class SiteSettings(models.Model):
    """Key-value site settings managed from admin dashboard."""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get_setting(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_setting(cls, key, value, user=None, description=None):
        obj, _ = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'updated_by': user, 'description': description or ''}
        )
        return obj


class UserWarning(models.Model):
    """Warnings issued to InstaUsers by admins."""
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    user = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name='warnings')
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_warnings')
    reason = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='low')
    is_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Warning to {self.user.username} ({self.get_severity_display()})"


class UserSuspension(models.Model):
    """Suspension/ban records for InstaUsers."""
    ACTION_CHOICES = (
        ('suspend', 'Suspended'),
        ('ban', 'Banned'),
        ('deactivate', 'Deactivated'),
    )

    user = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name='suspensions')
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    reason = models.TextField()
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_suspensions')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    lifted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lifted_suspensions')
    lifted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} — {self.user.username}"


class UserVerificationStatus(models.Model):
    """Tracks whether an InstaUser is verified (blue badge)."""
    user = models.OneToOneField(InstaUser, on_delete=models.CASCADE, related_name='verification_status')
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {'Verified' if self.is_verified else 'Not Verified'}"


class PostModeration(models.Model):
    """Moderation state for posts."""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('hidden', 'Hidden'),
        ('featured', 'Featured'),
        ('archived', 'Archived'),
        ('pinned', 'Pinned'),
        ('deleted', 'Deleted'),
    )

    post = models.OneToOneField(InstaPost, on_delete=models.CASCADE, related_name='moderation')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    moderation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post {self.post_id} — {self.get_status_display()}"


# ─── Signals ─────────────────────────────────────────────────────────────────
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_admin_profile(sender, instance, created, **kwargs):
    """Auto-creates AdminProfile for superusers and staff users."""
    if created and (instance.is_superuser or instance.is_staff):
        role = 'super_admin' if instance.is_superuser else 'viewer'
        AdminProfile.objects.get_or_create(user=instance, defaults={'role': role})
    elif not created and (instance.is_superuser or instance.is_staff):
        try:
            instance.admin_profile.save()
        except AdminProfile.DoesNotExist:
            role = 'super_admin' if instance.is_superuser else 'viewer'
            AdminProfile.objects.get_or_create(user=instance, defaults={'role': role})

