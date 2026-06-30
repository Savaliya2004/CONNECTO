
from django.db import models
import math
from django.utils import timezone 
from datetime import timedelta

# Create your models here.
class InstaUser(models.Model):
    GENDER_CHOICES = (
        ('male','Male'),
        ('female','Female'),
    )

    # ACCOUNT_TYPE = (
    #     ('private','Private'),
    #     ('public','Public'),
    # )
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    profile_pic = models.FileField(upload_to='profile_pics/', blank=True, null=True)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES,blank=True, null=True)
    name = models.CharField(max_length=100,blank=True, null=True)
    # account = models.CharField(max_length=20,choices=ACCOUNT_TYPE,default='private')
    bio = models.TextField(blank=True, null=True)
    otp = models.PositiveBigIntegerField(default = 456)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class InstaPost(models.Model):
    user = models.ForeignKey(InstaUser, on_delete=models.CASCADE)
    image = models.FileField(upload_to='InstaPost/')
    caption = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    tagged_users = models.ManyToManyField(InstaUser, blank=True, related_name='tagged_post')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.caption
    
    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + " second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
             
            if minutes == 1:
                return str(minutes) + " minute ago"
            
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)

            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"
            
            else:
                return str(years) + " years ago"
            

class Follow(models.Model):
    following = models.ForeignKey(InstaUser,on_delete=models.CASCADE,related_name="following")
    following_person = models.ForeignKey(InstaUser,on_delete=models.CASCADE,related_name="following_person")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.following.name} - following{self.following_person.name}"
     
class Notifications(models.Model):
    noti_choice = (
        ('follow','Follow'),
        ('comment','Comment'),
        ('like','Like'),
    )

    sender = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name="send")
    receiver = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name="receive")
    message = models.CharField(max_length=40,null = True,blank = True)
    notification_type = models.CharField(max_length=50,choices=noti_choice)  
    post_fk = models.ForeignKey(InstaPost,on_delete=models.CASCADE,null=True,blank=True)
    read_status = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.notification_type})"
    

    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + " second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
             
            if minutes == 1:
                return str(minutes) + " minute ago"
            
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)

            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"
            
            else:
                return str(years) + " years ago"
    
    def __str__(self):
        return f"{self.sender.username} {self.message} {self.receiver.username}"
    
class Like_Unlike(models.Model):
    user_fk = models.ForeignKey(InstaUser,on_delete=models.CASCADE , related_name="liked_by")
    post_fk = models.ForeignKey(InstaPost,on_delete=models.CASCADE , related_name="liked_post")
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ['user_fk','post_fk']

    def __str__(self):
        return f"{self.user_fk.username} liked{self.post_fk.caption}"


class InstaReels(models.Model):
    user = models.ForeignKey(InstaUser, on_delete=models.CASCADE)
    video = models.FileField(upload_to='InstaReels/')
    caption = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption
    
    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
             
            if minutes == 1:
                return str(minutes) + " minute ago"
            
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)

            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"
            
            else:
                return str(years) + " years ago"
            

class InstaStory(models.Model):
    user = models.ForeignKey(InstaUser,on_delete=models.CASCADE,related_name = "story_by")
    image = models.FileField(upload_to="InstaStory/", blank=True, null=True)
    video = models.FileField(upload_to='InstaStory/', blank=True, null=True)
    music = models.FileField(upload_to='InstaStory/music/', blank=True, null=True)
    caption = models.TextField(blank=True,null=True)
    duration = models.IntegerField(blank=True,null=True)
    audience = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    is_expired = models.BooleanField(null=True,blank=True,default = False)

    def save(self, *args,**kwargs):
        self.expired_at = timezone.now() + timedelta(hours = 24)
        return super().save(*args,**kwargs)
    
    def is_expired(self):
        if self.expired_at > timezone.now():
            self.is_expired = True

class ChatRoom(models.Model):
    user1 = models.ForeignKey(InstaUser,on_delete = models.CASCADE,related_name='user_1_chat')
    user2 = models.ForeignKey(InstaUser,on_delete = models.CASCADE,related_name='user_2_chat')

    created_at = models.DateTimeField(auto_now_add=True)

class Messages(models.Model):
    chat_room = models.ForeignKey(ChatRoom,on_delete = models.CASCADE,related_name='chatroom', null=True, blank=True)
    sender = models.ForeignKey(InstaUser, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    text_mssg = models.CharField(max_length=100, null=True, blank=True)
    image = models.FileField(null=True,blank=True)
    video = models.FileField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Comment(models.Model):
    user = models.ForeignKey(InstaUser, on_delete=models.CASCADE)
    post = models.ForeignKey(InstaPost, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    reel = models.ForeignKey(InstaReels, on_delete=models.CASCADE, null=True, blank=True, related_name='reel_comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.comment_text[:20]}"

