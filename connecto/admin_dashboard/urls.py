from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Auth
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),

    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/action/', views.user_action, name='user_action'),

    # Posts
    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:post_id>/action/', views.post_action, name='post_action'),

    # Stories
    path('stories/', views.story_list, name='story_list'),
    path('stories/<int:story_id>/delete/', views.story_delete, name='story_delete'),

    # Reels
    path('reels/', views.reel_list, name='reel_list'),
    path('reels/<int:reel_id>/delete/', views.reel_delete, name='reel_delete'),

    # Comments
    path('comments/', views.comment_list, name='comment_list'),
    path('comments/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),

    # Messages
    path('messages/', views.messages_list, name='messages_list'),

    # Reports
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/action/', views.report_action, name='report_action'),

    # Verification
    path('verification/', views.verification_list, name='verification_list'),
    path('verification/<int:verif_id>/action/', views.verification_action, name='verification_action'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),

    # Notifications
    path('notifications/', views.notifications_send, name='notifications_send'),

    # Hashtags
    path('hashtags/', views.hashtag_list, name='hashtag_list'),

    # Activity Logs
    path('logs/', views.activity_logs, name='activity_logs'),

    # Settings
    path('settings/', views.site_settings, name='site_settings'),

    # Global Search
    path('search/', views.global_search, name='global_search'),

    # CSV Export
    path('export/<str:model_name>/', views.export_csv, name='export_csv'),
]
