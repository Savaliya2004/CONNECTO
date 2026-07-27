from django import forms
from django.contrib.auth.models import User
from myapp.models import InstaUser
from .models import AdminProfile, Report, VerificationRequest, AdminNotification, SiteSettings, UserWarning


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'admin-input',
            'placeholder': 'Admin Username',
            'autocomplete': 'username',
            'id': 'id_admin_username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'admin-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
            'id': 'id_admin_password',
        })
    )


class UserEditForm(forms.ModelForm):
    """Form to edit InstaUser details from admin dashboard."""
    class Meta:
        model = InstaUser
        fields = ['username', 'email', 'name', 'bio', 'description', 'link', 'gender']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'admin-input', 'id': 'id_edit_username'}),
            'email': forms.EmailInput(attrs={'class': 'admin-input', 'id': 'id_edit_email'}),
            'name': forms.TextInput(attrs={'class': 'admin-input', 'id': 'id_edit_name'}),
            'bio': forms.Textarea(attrs={'class': 'admin-input', 'rows': 3, 'id': 'id_edit_bio'}),
            'description': forms.Textarea(attrs={'class': 'admin-input', 'rows': 3, 'id': 'id_edit_description'}),
            'link': forms.URLInput(attrs={'class': 'admin-input', 'id': 'id_edit_link'}),
            'gender': forms.Select(attrs={'class': 'admin-select', 'id': 'id_edit_gender'}),
        }


class SendNotificationForm(forms.ModelForm):
    class Meta:
        model = AdminNotification
        fields = ['notification_type', 'title', 'message', 'target']
        widgets = {
            'notification_type': forms.Select(attrs={'class': 'admin-select', 'id': 'id_notif_type'}),
            'title': forms.TextInput(attrs={'class': 'admin-input', 'placeholder': 'Notification Title', 'id': 'id_notif_title'}),
            'message': forms.Textarea(attrs={'class': 'admin-input', 'rows': 5, 'placeholder': 'Write your message...', 'id': 'id_notif_message'}),
            'target': forms.Select(attrs={'class': 'admin-select', 'id': 'id_notif_target'}),
        }


class ReportActionForm(forms.Form):
    ACTION_CHOICES = (
        ('reviewed', 'Mark as Reviewed'),
        ('dismissed', 'Dismiss Report'),
        ('action_taken', 'Action Taken'),
    )
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'admin-select', 'id': 'id_report_action'})
    )
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'admin-input', 'rows': 3, 'placeholder': 'Admin notes (optional)', 'id': 'id_report_notes'})
    )


class VerificationActionForm(forms.Form):
    ACTION_CHOICES = (
        ('approved', 'Approve Verification'),
        ('rejected', 'Reject Verification'),
        ('more_info', 'Request More Information'),
    )
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'admin-select', 'id': 'id_verif_action'})
    )
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'admin-input', 'rows': 3, 'placeholder': 'Notes for the user', 'id': 'id_verif_notes'})
    )


class UserActionForm(forms.Form):
    ACTION_CHOICES = (
        ('suspend', 'Suspend User'),
        ('ban', 'Ban User'),
        ('activate', 'Activate User'),
        ('delete', 'Delete User'),
        ('warn', 'Issue Warning'),
        ('verify', 'Verify Account'),
        ('unverify', 'Remove Verification'),
        ('reset_password', 'Reset Password'),
    )
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'admin-select', 'id': 'id_user_action'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'admin-input', 'rows': 3, 'placeholder': 'Reason for this action', 'id': 'id_action_reason'})
    )


class PostActionForm(forms.Form):
    ACTION_CHOICES = (
        ('delete', 'Delete Post'),
        ('hide', 'Hide Post'),
        ('feature', 'Feature Post'),
        ('restore', 'Restore Post'),
        ('archive', 'Archive Post'),
        ('pin', 'Pin Post'),
    )
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'admin-select', 'id': 'id_post_action'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'admin-input', 'rows': 2, 'placeholder': 'Reason (optional)', 'id': 'id_post_reason'})
    )


class SiteSettingsForm(forms.Form):
    site_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'admin-input', 'id': 'id_site_name'})
    )
    maintenance_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'admin-checkbox', 'id': 'id_maintenance_mode'})
    )
    allow_registration = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'admin-checkbox', 'id': 'id_allow_registration'})
    )
    max_post_size_mb = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'admin-input', 'id': 'id_max_post_size'})
    )
    support_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'admin-input', 'id': 'id_support_email'})
    )
    password_min_length = forms.IntegerField(
        required=False,
        min_value=4,
        max_value=32,
        widget=forms.NumberInput(attrs={'class': 'admin-input', 'id': 'id_pw_min_length'})
    )
