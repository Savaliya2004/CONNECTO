"""
Service Layer for the CONNECTO Admin Dashboard.
All heavy ORM queries live here — views stay thin.
Uses select_related() and prefetch_related() throughout.
"""
import re
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from myapp.models import (
    InstaUser, InstaPost, Follow, Notifications,
    Like_Unlike, InstaReels, InstaStory, ChatRoom, Messages, Comment
)
from .models import (
    Report, VerificationRequest, AdminActivityLog,
    UserSuspension, UserWarning, PostModeration, AdminNotification
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def paginate(queryset, page, per_page=20):
    paginator = Paginator(queryset, per_page)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


# ─── Activity Logging ─────────────────────────────────────────────────────────

class ActivityService:
    @staticmethod
    def log(request, action, target_type=None, target_id=None, target_label=None, details=None):
        try:
            AdminActivityLog.objects.create(
                admin=request.user if request.user.is_authenticated else None,
                action=action,
                target_type=target_type,
                target_id=target_id,
                target_label=target_label or '',
                details=details or '',
                ip_address=_get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        except Exception:
            pass

    @staticmethod
    def get_logs(filters=None, page=1):
        qs = AdminActivityLog.objects.select_related('admin').order_by('-created_at')
        if filters:
            if filters.get('action'):
                qs = qs.filter(action=filters['action'])
            if filters.get('admin_id'):
                qs = qs.filter(admin_id=filters['admin_id'])
            if filters.get('date_from'):
                qs = qs.filter(created_at__date__gte=filters['date_from'])
            if filters.get('date_to'):
                qs = qs.filter(created_at__date__lte=filters['date_to'])
        return paginate(qs, page, 30)


# ─── Dashboard Statistics ─────────────────────────────────────────────────────

class DashboardService:
    @staticmethod
    def get_stats():
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)

        stats = {
            # Users
            'total_users': InstaUser.objects.count(),
            'active_users_today': InstaUser.objects.filter(updated_at__date=today).count(),
            'new_users_week': InstaUser.objects.filter(created_at__gte=week_ago).count(),
            # Posts
            'total_posts': InstaPost.objects.count(),
            'posts_today': InstaPost.objects.filter(created_at__date=today).count(),
            # Stories
            'stories_today': InstaStory.objects.filter(created_at__date=today).count(),
            'total_stories': InstaStory.objects.count(),
            # Reels
            'reels_today': InstaReels.objects.filter(created_at__date=today).count(),
            'total_reels': InstaReels.objects.count(),
            # Engagement
            'total_comments': Comment.objects.count(),
            'total_likes': Like_Unlike.objects.count(),
            # Social
            'total_followers': Follow.objects.count(),
            'total_following': Follow.objects.count(),
            # Messages
            'total_messages': Messages.objects.count(),
            # Notifications
            'total_notifications': Notifications.objects.count(),
            # Moderation
            'pending_reports': Report.objects.filter(status='pending').count(),
            'pending_verifications': VerificationRequest.objects.filter(status='pending').count(),
        }
        return stats

    @staticmethod
    def get_chart_data(period='weekly'):
        """Returns chart data for users, posts, etc. for the given period."""
        now = timezone.now()
        labels = []
        user_counts = []
        post_counts = []
        like_counts = []
        comment_counts = []

        if period == 'daily':
            days = 14
            for i in range(days - 1, -1, -1):
                day = now - timedelta(days=i)
                date = day.date()
                labels.append(date.strftime('%b %d'))
                user_counts.append(InstaUser.objects.filter(created_at__date=date).count())
                post_counts.append(InstaPost.objects.filter(created_at__date=date).count())
                like_counts.append(Like_Unlike.objects.filter(created_at__date=date).count())
                comment_counts.append(Comment.objects.filter(created_at__date=date).count())

        elif period == 'weekly':
            weeks = 12
            for i in range(weeks - 1, -1, -1):
                week_start = now - timedelta(weeks=i + 1)
                week_end = now - timedelta(weeks=i)
                labels.append(f"W{weeks - i}")
                user_counts.append(InstaUser.objects.filter(created_at__range=(week_start, week_end)).count())
                post_counts.append(InstaPost.objects.filter(created_at__range=(week_start, week_end)).count())
                like_counts.append(Like_Unlike.objects.filter(created_at__range=(week_start, week_end)).count())
                comment_counts.append(Comment.objects.filter(created_at__range=(week_start, week_end)).count())

        elif period == 'monthly':
            months = 12
            for i in range(months - 1, -1, -1):
                month_date = now - timedelta(days=30 * i)
                labels.append(month_date.strftime('%b %Y'))
                month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if i > 0:
                    next_month = now - timedelta(days=30 * (i - 1))
                    month_end = next_month.replace(day=1)
                else:
                    month_end = now
                user_counts.append(InstaUser.objects.filter(created_at__range=(month_start, month_end)).count())
                post_counts.append(InstaPost.objects.filter(created_at__range=(month_start, month_end)).count())
                like_counts.append(Like_Unlike.objects.filter(created_at__range=(month_start, month_end)).count())
                comment_counts.append(Comment.objects.filter(created_at__range=(month_start, month_end)).count())

        return {
            'labels': labels,
            'datasets': {
                'users': user_counts,
                'posts': post_counts,
                'likes': like_counts,
                'comments': comment_counts,
            }
        }

    @staticmethod
    def get_top_users(limit=10):
        return InstaUser.objects.annotate(
            follower_count=Count('following_person', distinct=True),
            post_count=Count('instapost', distinct=True),
        ).order_by('-follower_count')[:limit]

    @staticmethod
    def get_most_liked_posts(limit=10):
        return InstaPost.objects.select_related('user').annotate(
            like_count=Count('liked_post', distinct=True),
            comment_count=Count('comments', distinct=True),
        ).order_by('-like_count')[:limit]

    @staticmethod
    def get_trending_hashtags(limit=10):
        """Extract and count hashtags from post captions."""
        posts = InstaPost.objects.exclude(caption__isnull=True).exclude(caption='').values_list('caption', flat=True)
        hashtag_counts = {}
        for caption in posts:
            tags = re.findall(r'#(\w+)', caption.lower())
            for tag in tags:
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'tag': tag, 'count': count} for tag, count in sorted_tags[:limit]]

    @staticmethod
    def get_recent_registrations(limit=10):
        return InstaUser.objects.order_by('-created_at')[:limit]

    @staticmethod
    def get_most_reported_posts(limit=10):
        return InstaPost.objects.select_related('user').annotate(
            report_count=Count('reports', distinct=True)
        ).filter(report_count__gt=0).order_by('-report_count')[:limit]


# ─── User Service ─────────────────────────────────────────────────────────────

class UserService:
    @staticmethod
    def get_users_table(filters=None, page=1, per_page=20):
        qs = InstaUser.objects.annotate(
            follower_count=Count('following_person', distinct=True),
            following_count=Count('following', distinct=True),
            post_count=Count('instapost', distinct=True),
            story_count=Count('story_by', distinct=True),
        ).order_by('-created_at')

        if filters:
            q = filters.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(username__icontains=q) |
                    Q(email__icontains=q) |
                    Q(name__icontains=q)
                )
            if filters.get('date_from'):
                qs = qs.filter(created_at__date__gte=filters['date_from'])
            if filters.get('date_to'):
                qs = qs.filter(created_at__date__lte=filters['date_to'])
            sort = filters.get('sort', '-created_at')
            allowed_sorts = ['created_at', '-created_at', 'username', '-username', '-follower_count', '-post_count']
            if sort in allowed_sorts:
                qs = qs.order_by(sort)

        return paginate(qs, page, per_page)

    @staticmethod
    def get_user_detail(user_id):
        user = InstaUser.objects.get(id=user_id)
        posts = InstaPost.objects.filter(user=user).order_by('-created_at')
        stories = InstaStory.objects.filter(user=user).order_by('-created_at')
        followers = Follow.objects.filter(following_person=user).select_related('following')
        following = Follow.objects.filter(following=user).select_related('following_person')
        comments = Comment.objects.filter(user=user).select_related('post').order_by('-created_at')[:20]
        reports = Report.objects.filter(reported_user=user).select_related('reporter', 'reviewed_by').order_by('-created_at')
        warnings = UserWarning.objects.filter(user=user).select_related('issued_by').order_by('-created_at')
        suspensions = UserSuspension.objects.filter(user=user).select_related('issued_by').order_by('-created_at')
        activity_logs = AdminActivityLog.objects.filter(
            target_type='user', target_id=user_id
        ).select_related('admin').order_by('-created_at')[:20]

        active_suspension = suspensions.filter(is_active=True).first()

        try:
            verification_status = user.verification_status
        except Exception:
            verification_status = None

        return {
            'user': user,
            'posts': posts,
            'stories': stories,
            'followers': followers,
            'following': following,
            'comments': comments,
            'reports': reports,
            'warnings': warnings,
            'suspensions': suspensions,
            'activity_logs': activity_logs,
            'active_suspension': active_suspension,
            'verification_status': verification_status,
            'follower_count': followers.count(),
            'following_count': following.count(),
            'post_count': posts.count(),
            'story_count': stories.count(),
        }


# ─── Content Service ──────────────────────────────────────────────────────────

class ContentService:
    @staticmethod
    def get_posts(filters=None, page=1, per_page=20):
        qs = InstaPost.objects.select_related('user').annotate(
            like_count=Count('liked_post', distinct=True),
            comment_count=Count('comments', distinct=True),
            report_count=Count('reports', distinct=True),
        ).order_by('-created_at')

        if filters:
            q = filters.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(caption__icontains=q) |
                    Q(user__username__icontains=q) |
                    Q(location__icontains=q)
                )
            if filters.get('date_from'):
                qs = qs.filter(created_at__date__gte=filters['date_from'])
            if filters.get('date_to'):
                qs = qs.filter(created_at__date__lte=filters['date_to'])
            sort = filters.get('sort', '-created_at')
            allowed = ['-created_at', 'created_at', '-like_count', '-comment_count', '-report_count']
            if sort in allowed:
                qs = qs.order_by(sort)

        return paginate(qs, page, per_page)

    @staticmethod
    def get_stories(filters=None, page=1, per_page=20):
        qs = InstaStory.objects.select_related('user').order_by('-created_at')
        if filters:
            q = filters.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(user__username__icontains=q) |
                    Q(caption__icontains=q)
                )
        return paginate(qs, page, per_page)

    @staticmethod
    def get_reels(filters=None, page=1, per_page=20):
        qs = InstaReels.objects.select_related('user').annotate(
            comment_count=Count('reel_comments', distinct=True),
        ).order_by('-created_at')
        if filters:
            q = filters.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(user__username__icontains=q) |
                    Q(caption__icontains=q)
                )
        return paginate(qs, page, per_page)

    @staticmethod
    def get_comments(filters=None, page=1, per_page=30):
        qs = Comment.objects.select_related('user', 'post', 'reel').order_by('-created_at')
        if filters:
            q = filters.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(comment_text__icontains=q) |
                    Q(user__username__icontains=q)
                )
        return paginate(qs, page, per_page)

    @staticmethod
    def get_messages_overview(filters=None, page=1, per_page=20):
        qs = ChatRoom.objects.select_related('user1', 'user2').annotate(
            message_count=Count('chatroom', distinct=True)
        ).order_by('-created_at')
        return paginate(qs, page, per_page)

    @staticmethod
    def get_hashtags(filters=None, page=1, per_page=30):
        posts = InstaPost.objects.exclude(caption__isnull=True).exclude(caption='').values_list('caption', flat=True)
        hashtag_counts = {}
        for caption in posts:
            tags = re.findall(r'#(\w+)', caption.lower())
            for tag in tags:
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        q = filters.get('q', '').strip().lower() if filters else ''
        sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        if q:
            sorted_tags = [(t, c) for t, c in sorted_tags if q in t]
        result = [{'tag': tag, 'count': count} for tag, count in sorted_tags]
        paginator = Paginator(result, per_page)
        try:
            return paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            return paginator.page(1)


# ─── Report Service ───────────────────────────────────────────────────────────

class ReportService:
    @staticmethod
    def get_reports(filters=None, page=1, per_page=20):
        qs = Report.objects.select_related(
            'reporter', 'reported_user', 'reported_post', 'reviewed_by'
        ).order_by('-created_at')

        if filters:
            if filters.get('status'):
                qs = qs.filter(status=filters['status'])
            if filters.get('reason'):
                qs = qs.filter(reason=filters['reason'])
            q = filters.get('q', '').strip()
            if q:
                qs = qs.filter(
                    Q(reporter__username__icontains=q) |
                    Q(reported_user__username__icontains=q)
                )

        return paginate(qs, page, per_page)


# ─── Verification Service ─────────────────────────────────────────────────────

class VerificationService:
    @staticmethod
    def get_requests(filters=None, page=1, per_page=20):
        qs = VerificationRequest.objects.select_related('user', 'reviewed_by').order_by('-created_at')
        if filters and filters.get('status'):
            qs = qs.filter(status=filters['status'])
        return paginate(qs, page, per_page)


# ─── Global Search Service ────────────────────────────────────────────────────

class SearchService:
    @staticmethod
    def search(query, limit=10):
        if not query or len(query) < 2:
            return {}

        q = query.strip()
        return {
            'users': list(InstaUser.objects.filter(
                Q(username__icontains=q) | Q(email__icontains=q) | Q(name__icontains=q)
            )[:limit]),
            'posts': list(InstaPost.objects.select_related('user').filter(
                Q(caption__icontains=q) | Q(location__icontains=q)
            )[:limit]),
            'comments': list(Comment.objects.select_related('user', 'post').filter(
                comment_text__icontains=q
            )[:limit]),
        }
