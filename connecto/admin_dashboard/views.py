"""
Views for the CONNECTO Admin Dashboard.
All views (except login) require Django staff/superuser authentication.
Uses service layer for all ORM queries.
"""
import csv
import json
from datetime import timedelta

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from myapp.models import (
    InstaUser, InstaPost, Follow, Like_Unlike,
    InstaReels, InstaStory, Comment, Messages, ChatRoom
)
from .forms import (
    AdminLoginForm, UserEditForm, SendNotificationForm,
    ReportActionForm, VerificationActionForm, UserActionForm,
    PostActionForm, SiteSettingsForm
)
from .models import (
    AdminProfile, Report, VerificationRequest, AdminNotification,
    AdminActivityLog, SiteSettings, UserWarning, UserSuspension,
    UserVerificationStatus, PostModeration
)
from .permissions import admin_required, get_permissions_context
from .services import (
    DashboardService, UserService, ContentService,
    ReportService, VerificationService, ActivityService, SearchService
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _base_context(request):
    """Base context injected into every admin template."""
    ctx = get_permissions_context(request.user)
    ctx['pending_reports'] = Report.objects.filter(status='pending').count()
    ctx['pending_verifications'] = VerificationRequest.objects.filter(status='pending').count()
    return ctx


# ─── Auth Views ───────────────────────────────────────────────────────────────

def admin_login(request):
    """Redirect to the single unified login page."""
    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(f'/login/?next={next_url}')
    return redirect('/login/')


@admin_required
def admin_logout(request):
    ActivityService.log(request, 'logout')
    auth_logout(request)
    return redirect('admin_dashboard:login')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin_required
def dashboard(request):
    stats = DashboardService.get_stats()
    top_users = DashboardService.get_top_users(8)
    most_liked = DashboardService.get_most_liked_posts(6)
    trending_tags = DashboardService.get_trending_hashtags(10)
    recent_users = DashboardService.get_recent_registrations(8)
    most_reported = DashboardService.get_most_reported_posts(5)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Dashboard',
        'active_nav': 'dashboard',
        'stats': stats,
        'top_users': top_users,
        'most_liked': most_liked,
        'trending_tags': trending_tags,
        'recent_users': recent_users,
        'most_reported': most_reported,
    })
    return render(request, 'admin_dashboard/dashboard.html', ctx)


@admin_required
def analytics_api(request):
    """JSON endpoint for Chart.js chart data."""
    period = request.GET.get('period', 'weekly')
    if period not in ('daily', 'weekly', 'monthly'):
        period = 'weekly'
    data = DashboardService.get_chart_data(period)
    return JsonResponse(data)


# ─── User Management ──────────────────────────────────────────────────────────

@admin_required
def user_list(request):
    filters = {
        'q': request.GET.get('q', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'sort': request.GET.get('sort', '-created_at'),
    }
    page = request.GET.get('page', 1)
    users = UserService.get_users_table(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'User Management',
        'active_nav': 'users',
        'users': users,
        'filters': filters,
        'total_users': InstaUser.objects.count(),
    })
    return render(request, 'admin_dashboard/users/list.html', ctx)


@admin_required
def user_detail(request, user_id):
    try:
        data = UserService.get_user_detail(user_id)
    except InstaUser.DoesNotExist:
        return redirect('admin_dashboard:user_list')

    ctx = _base_context(request)
    ctx.update({
        'page_title': f"User: {data['user'].username}",
        'active_nav': 'users',
        **data,
    })
    return render(request, 'admin_dashboard/users/detail.html', ctx)


@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(InstaUser, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            ActivityService.log(
                request, 'user_edit',
                target_type='user', target_id=user_id,
                target_label=user.username,
                details='User profile updated via admin dashboard'
            )
            return redirect('admin_dashboard:user_detail', user_id=user_id)
    else:
        form = UserEditForm(instance=user)

    ctx = _base_context(request)
    ctx.update({
        'page_title': f"Edit User: {user.username}",
        'active_nav': 'users',
        'user_obj': user,
        'form': form,
    })
    return render(request, 'admin_dashboard/users/edit.html', ctx)


@admin_required
@require_POST
def user_action(request, user_id):
    user = get_object_or_404(InstaUser, id=user_id)
    form = UserActionForm(request.POST)

    if form.is_valid():
        action = form.cleaned_data['action']
        reason = form.cleaned_data.get('reason', '')

        if action == 'suspend':
            UserSuspension.objects.create(
                user=user, action='suspend',
                reason=reason, issued_by=request.user
            )
            ActivityService.log(request, 'user_suspend', 'user', user_id, user.username, reason)

        elif action == 'ban':
            UserSuspension.objects.create(
                user=user, action='ban',
                reason=reason, issued_by=request.user
            )
            ActivityService.log(request, 'user_ban', 'user', user_id, user.username, reason)

        elif action == 'activate':
            UserSuspension.objects.filter(user=user, is_active=True).update(
                is_active=False, lifted_by=request.user, lifted_at=timezone.now()
            )
            ActivityService.log(request, 'user_activate', 'user', user_id, user.username)

        elif action == 'delete':
            username = user.username
            user.delete()
            ActivityService.log(request, 'user_delete', 'user', user_id, username, reason)
            return redirect('admin_dashboard:user_list')

        elif action == 'warn':
            UserWarning.objects.create(
                user=user, issued_by=request.user,
                reason=reason, severity='medium'
            )
            ActivityService.log(request, 'user_edit', 'user', user_id, user.username, f'Warning issued: {reason}')

        elif action == 'verify':
            vs, _ = UserVerificationStatus.objects.get_or_create(user=user)
            vs.is_verified = True
            vs.verified_by = request.user
            vs.verified_at = timezone.now()
            vs.save()
            ActivityService.log(request, 'verification_approve', 'user', user_id, user.username)

        elif action == 'unverify':
            try:
                vs = user.verification_status
                vs.is_verified = False
                vs.save()
            except UserVerificationStatus.DoesNotExist:
                pass
            ActivityService.log(request, 'verification_reject', 'user', user_id, user.username)

        elif action == 'reset_password':
            # Generate a temporary password and log
            temp_pw = User.objects.make_random_password()
            user.password = make_password(temp_pw)
            user.save()
            ActivityService.log(request, 'password_reset', 'user', user_id, user.username, f'Temp: {temp_pw}')

    return redirect('admin_dashboard:user_detail', user_id=user_id)


# ─── Content: Posts ──────────────────────────────────────────────────────────

@admin_required
def post_list(request):
    filters = {
        'q': request.GET.get('q', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'sort': request.GET.get('sort', '-created_at'),
    }
    page = request.GET.get('page', 1)
    posts = ContentService.get_posts(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Post Management',
        'active_nav': 'posts',
        'posts': posts,
        'filters': filters,
        'post_action_form': PostActionForm(),
        'total_posts': InstaPost.objects.count(),
    })
    return render(request, 'admin_dashboard/posts/list.html', ctx)


@admin_required
@require_POST
def post_action(request, post_id):
    post = get_object_or_404(InstaPost, id=post_id)
    form = PostActionForm(request.POST)

    if form.is_valid():
        action = form.cleaned_data['action']
        reason = form.cleaned_data.get('reason', '')

        if action == 'delete':
            caption = post.caption or f'Post #{post_id}'
            post.delete()
            ActivityService.log(request, 'post_delete', 'post', post_id, caption, reason)
            return redirect('admin_dashboard:post_list')
        else:
            status_map = {
                'hide': 'hidden', 'feature': 'featured',
                'restore': 'active', 'archive': 'archived', 'pin': 'pinned'
            }
            if action in status_map:
                moderation, _ = PostModeration.objects.get_or_create(post=post)
                moderation.status = status_map[action]
                moderation.moderated_by = request.user
                moderation.moderation_reason = reason
                moderation.save()
                ActivityService.log(
                    request, 'post_hide' if action == 'hide' else 'post_feature',
                    'post', post_id, post.caption or f'Post #{post_id}', reason
                )

    return redirect('admin_dashboard:post_list')


# ─── Content: Stories ─────────────────────────────────────────────────────────

@admin_required
def story_list(request):
    filters = {'q': request.GET.get('q', '')}
    page = request.GET.get('page', 1)
    stories = ContentService.get_stories(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Story Management',
        'active_nav': 'stories',
        'stories': stories,
        'filters': filters,
        'total_stories': InstaStory.objects.count(),
    })
    return render(request, 'admin_dashboard/stories/list.html', ctx)


@admin_required
@require_POST
def story_delete(request, story_id):
    story = get_object_or_404(InstaStory, id=story_id)
    story.delete()
    ActivityService.log(request, 'post_delete', 'story', story_id, f'Story by {story.user.username}')
    return redirect('admin_dashboard:story_list')


# ─── Content: Reels ───────────────────────────────────────────────────────────

@admin_required
def reel_list(request):
    filters = {'q': request.GET.get('q', '')}
    page = request.GET.get('page', 1)
    reels = ContentService.get_reels(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Reel Management',
        'active_nav': 'reels',
        'reels': reels,
        'filters': filters,
        'total_reels': InstaReels.objects.count(),
    })
    return render(request, 'admin_dashboard/reels/list.html', ctx)


@admin_required
@require_POST
def reel_delete(request, reel_id):
    reel = get_object_or_404(InstaReels, id=reel_id)
    reel.delete()
    ActivityService.log(request, 'post_delete', 'reel', reel_id, f'Reel by {reel.user.username}')
    return redirect('admin_dashboard:reel_list')


# ─── Content: Comments ────────────────────────────────────────────────────────

@admin_required
def comment_list(request):
    filters = {'q': request.GET.get('q', '')}
    page = request.GET.get('page', 1)
    comments = ContentService.get_comments(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Comment Management',
        'active_nav': 'comments',
        'comments': comments,
        'filters': filters,
        'total_comments': Comment.objects.count(),
    })
    return render(request, 'admin_dashboard/comments/list.html', ctx)


@admin_required
@require_POST
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    ActivityService.log(request, 'comment_delete', 'comment', comment_id)
    return redirect('admin_dashboard:comment_list')


# ─── Messages ─────────────────────────────────────────────────────────────────

@admin_required
def messages_list(request):
    page = request.GET.get('page', 1)
    chat_rooms = ContentService.get_messages_overview(page=page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Messages Overview',
        'active_nav': 'messages',
        'chat_rooms': chat_rooms,
        'total_messages': Messages.objects.count(),
    })
    return render(request, 'admin_dashboard/messages/list.html', ctx)


# ─── Reports & Moderation ─────────────────────────────────────────────────────

@admin_required
def report_list(request):
    filters = {
        'status': request.GET.get('status', ''),
        'reason': request.GET.get('reason', ''),
        'q': request.GET.get('q', ''),
    }
    page = request.GET.get('page', 1)
    reports = ReportService.get_reports(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Reports & Moderation',
        'active_nav': 'reports',
        'reports': reports,
        'filters': filters,
        'reason_choices': Report.REASON_CHOICES,
        'status_choices': Report.STATUS_CHOICES,
        'total_pending': Report.objects.filter(status='pending').count(),
        'action_form': ReportActionForm(),
    })
    return render(request, 'admin_dashboard/reports/list.html', ctx)


@admin_required
@require_POST
def report_action(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    form = ReportActionForm(request.POST)

    if form.is_valid():
        report.status = form.cleaned_data['action']
        report.admin_notes = form.cleaned_data.get('admin_notes', '')
        report.reviewed_by = request.user
        report.save()
        ActivityService.log(request, 'report_review', 'report', report_id,
                            f'Report by {report.reporter.username}',
                            f'Action: {form.cleaned_data["action"]}')

    return redirect('admin_dashboard:report_list')


# ─── Verification Requests ────────────────────────────────────────────────────

@admin_required
def verification_list(request):
    filters = {'status': request.GET.get('status', '')}
    page = request.GET.get('page', 1)
    verifications = VerificationService.get_requests(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Verification Requests',
        'active_nav': 'verification',
        'verifications': verifications,
        'filters': filters,
        'status_choices': VerificationRequest.STATUS_CHOICES,
        'total_pending': VerificationRequest.objects.filter(status='pending').count(),
        'action_form': VerificationActionForm(),
    })
    return render(request, 'admin_dashboard/verification/list.html', ctx)


@admin_required
@require_POST
def verification_action(request, verif_id):
    verif = get_object_or_404(VerificationRequest, id=verif_id)
    form = VerificationActionForm(request.POST)

    if form.is_valid():
        action = form.cleaned_data['action']
        verif.status = action
        verif.admin_notes = form.cleaned_data.get('admin_notes', '')
        verif.reviewed_by = request.user
        verif.save()

        if action == 'approved':
            vs, _ = UserVerificationStatus.objects.get_or_create(user=verif.user)
            vs.is_verified = True
            vs.verified_by = request.user
            vs.verified_at = timezone.now()
            vs.save()
            ActivityService.log(request, 'verification_approve', 'user',
                                verif.user.id, verif.user.username)
        else:
            ActivityService.log(request, 'verification_reject', 'user',
                                verif.user.id, verif.user.username, f'Action: {action}')

    return redirect('admin_dashboard:verification_list')


# ─── Analytics ────────────────────────────────────────────────────────────────

@admin_required
def analytics(request):
    stats = DashboardService.get_stats()
    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Analytics',
        'active_nav': 'analytics',
        'stats': stats,
    })
    return render(request, 'admin_dashboard/analytics/index.html', ctx)


# ─── Notifications ────────────────────────────────────────────────────────────

@admin_required
def notifications_send(request):
    form = SendNotificationForm()
    success = False

    if request.method == 'POST':
        form = SendNotificationForm(request.POST)
        if form.is_valid():
            notif = form.save(commit=False)
            notif.sent_by = request.user
            notif.save()
            ActivityService.log(request, 'notification_sent',
                                target_label=notif.title,
                                details=f'Type: {notif.notification_type}, Target: {notif.target}')
            success = True
            form = SendNotificationForm()

    recent = AdminNotification.objects.select_related('sent_by').order_by('-created_at')[:20]
    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Send Notifications',
        'active_nav': 'notifications',
        'form': form,
        'success': success,
        'recent_notifications': recent,
    })
    return render(request, 'admin_dashboard/notifications/send.html', ctx)


# ─── Hashtags ─────────────────────────────────────────────────────────────────

@admin_required
def hashtag_list(request):
    filters = {'q': request.GET.get('q', '')}
    page = request.GET.get('page', 1)
    hashtags = ContentService.get_hashtags(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Hashtag Management',
        'active_nav': 'hashtags',
        'hashtags': hashtags,
        'filters': filters,
    })
    return render(request, 'admin_dashboard/hashtags/list.html', ctx)


# ─── Activity Logs ────────────────────────────────────────────────────────────

@admin_required
def activity_logs(request):
    filters = {
        'action': request.GET.get('action', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
    }
    page = request.GET.get('page', 1)
    logs = ActivityService.get_logs(filters, page)

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Activity Logs',
        'active_nav': 'logs',
        'logs': logs,
        'filters': filters,
        'action_choices': AdminActivityLog.ACTION_CHOICES,
    })
    return render(request, 'admin_dashboard/logs/list.html', ctx)


# ─── Site Settings ────────────────────────────────────────────────────────────

@admin_required
def site_settings(request):
    # Load current settings
    current = {
        'site_name': SiteSettings.get_setting('site_name', 'CONNECTO'),
        'maintenance_mode': SiteSettings.get_setting('maintenance_mode', 'false') == 'true',
        'allow_registration': SiteSettings.get_setting('allow_registration', 'true') == 'true',
        'max_post_size_mb': SiteSettings.get_setting('max_post_size_mb', '10'),
        'support_email': SiteSettings.get_setting('support_email', ''),
        'password_min_length': SiteSettings.get_setting('password_min_length', '6'),
    }

    form = SiteSettingsForm(initial=current)
    success = False

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            SiteSettings.set_setting('site_name', d.get('site_name', 'CONNECTO'), request.user)
            SiteSettings.set_setting('maintenance_mode', 'true' if d.get('maintenance_mode') else 'false', request.user)
            SiteSettings.set_setting('allow_registration', 'true' if d.get('allow_registration') else 'false', request.user)
            if d.get('max_post_size_mb'):
                SiteSettings.set_setting('max_post_size_mb', str(d['max_post_size_mb']), request.user)
            if d.get('support_email'):
                SiteSettings.set_setting('support_email', d['support_email'], request.user)
            if d.get('password_min_length'):
                SiteSettings.set_setting('password_min_length', str(d['password_min_length']), request.user)
            ActivityService.log(request, 'settings_change', details='Site settings updated')
            success = True

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Site Settings',
        'active_nav': 'settings',
        'form': form,
        'success': success,
        'all_settings': SiteSettings.objects.all().order_by('key'),
    })
    return render(request, 'admin_dashboard/settings/index.html', ctx)


# ─── Global Search ────────────────────────────────────────────────────────────

@admin_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    results = SearchService.search(query) if query else {}

    ctx = _base_context(request)
    ctx.update({
        'page_title': 'Search Results',
        'active_nav': 'search',
        'query': query,
        'results': results,
    })
    return render(request, 'admin_dashboard/search/results.html', ctx)


# ─── Export CSV ───────────────────────────────────────────────────────────────

@admin_required
def export_csv(request, model_name):
    allowed = ['users', 'posts', 'reports', 'comments']
    if model_name not in allowed:
        return redirect('admin_dashboard:dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="connecto_{model_name}_{timezone.now().strftime("%Y%m%d")}.csv"'
    writer = csv.writer(response)

    if model_name == 'users':
        writer.writerow(['ID', 'Username', 'Email', 'Name', 'Gender', 'Joined'])
        for u in InstaUser.objects.all().values_list('id', 'username', 'email', 'name', 'gender', 'created_at'):
            writer.writerow(u)

    elif model_name == 'posts':
        writer.writerow(['ID', 'Username', 'Caption', 'Location', 'Created'])
        for p in InstaPost.objects.select_related('user').all():
            writer.writerow([p.id, p.user.username, p.caption or '', p.location or '', p.created_at])

    elif model_name == 'reports':
        writer.writerow(['ID', 'Reporter', 'Reported User', 'Reason', 'Status', 'Created'])
        for r in Report.objects.select_related('reporter', 'reported_user').all():
            writer.writerow([
                r.id, r.reporter.username,
                r.reported_user.username if r.reported_user else '',
                r.get_reason_display(), r.get_status_display(), r.created_at
            ])

    elif model_name == 'comments':
        writer.writerow(['ID', 'Username', 'Comment', 'Post ID', 'Created'])
        for c in Comment.objects.select_related('user', 'post').all():
            writer.writerow([c.id, c.user.username, c.comment_text, c.post_id or '', c.created_at])

    ActivityService.log(request, 'other', details=f'Exported CSV: {model_name}')
    return response
