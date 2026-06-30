"""
URL configuration for chillr_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('',views.home,name='home'),
    path('',views.home,name='home'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('profile/',views.profile,name='profile'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('settings/',views.settings,name='settings'),
    path('create-post/',views.create_post,name='create-post'),
    path('explore/',views.explore,name='explore'),
    path('notifications/',views.notifications,name='notifications'),
    path('logout/',views.logout,name='logout'),
    path('following/',views.following,name='following'),
    path('follow_unfollow/<int:pk>',views.follow_unfollow,name='follow_unfollow'),
    path('followers/',views.followers,name='followers'),
    path('remove_followers/<int:pk>',views.remove_followers,name='remove_followers'),
    path('like_unlike/<int:pk>',views.like_unlike,name="like_unlike"),
    path('upload_reel/',views.upload_reel,name='upload_reel'),
    path('reels/',views.reels,name='reels'),
    path('create_story/',views.create_story,name='create_story'),
    path('view_story/',views.view_story,name='view_story'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('messages/',views.messages,name='messages'),
    path('messages/<int:pk>',views.messages,name='messages'),
    path('send_message/<int:pk>',views.send_message,name='send_message'),
    path('add_comment/<int:pk>',views.add_comment,name='add_comment'),
    path('add_reel_comment/<int:pk>',views.add_reel_comment,name='add_reel_comment'),




]
