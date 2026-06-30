from django.shortcuts import render,redirect
from .models import * 
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q
from django.utils import timezone
from .utils import myCustomMail , get_or_create_chatRoom
import random
# Create your views here.

def checkLoggin(view_function):
    def wrapper(request,*args,**kwargs):
        if "email" in request.session:
            try:
                uid = InstaUser.objects.get(email = request.session['email'])
                request.uid = uid 
                return view_function(request,*args,**kwargs)
            except InstaUser.DoesNotExist:
                return redirect("login")
        return redirect("login")
    
    return wrapper

def login(request):
    if request.POST:
        email = request.POST['email']
        password =request.POST['password']

        try:
            uid = InstaUser.objects.get(email = email)
            if not check_password(password,uid.password):
                context = {
                    'e_msg' : "Invalid Credentials !"
                }
                return render(request,"myapp/login.html",context)
            else:
                request.session['email'] = email 
                context = { 'uid' : uid }
                print("----------->>> home",uid)
                return redirect("home")

        except:
            context = {
                'e_msg' : "User Not Found !"
            }
            return render(request,"myapp/login.html",context)

    return render(request,'myapp/login.html')

def signup(request):
    if request.POST:
        username = request.POST['username']
        email = request.POST['email']
        gender = request.POST['gender']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if InstaUser.objects.filter(username=username).exists():
            context = {
                'e_msg' : "Username Already exists !"
            }
            return render(request,"myapp/register.html",context)

        elif InstaUser.objects.filter(email = email).exists():
            context = {
                'e_msg' : "Email Already exists !"
            }
            return render(request,"myapp/register.html",context)

        elif password!= confirm_password:
            context = {
                'e_msg': "Password does not match !"
            }
            return render(request,"myapp/register.html",context)

        else:
            if gender == "male":
                img = "images/boy.png"
            elif gender == "female":
                img = "images/girl.png"

            InstaUser.objects.create(
                    username = username,
                    email = email,
                    password = make_password(password),
                    profile_pic = img ,
                    gender = gender
                    )
                    
            return redirect("login")

    return render(request,"myapp/register.html")

@checkLoggin
def home(request):
    uid = request.uid
    # post_all = InstaPost.objects.all() .order_by('-created_at')
    my_following_users =  Follow.objects.filter(following = uid).values_list("following_person",flat=True)
    # post_all = InstaPost.objects.filter(user = uid)
    post_all = InstaPost.objects.filter(user__in = list(my_following_users) + [uid.id]).order_by('-created_at')
    users = list(my_following_users) + [uid.id]
    story_all = InstaStory.objects.filter(
        user__in = users,
        expired_at__gt = timezone.now()
    ).order_by('user','-created_at')

    unique_stories = []
    seen_users = set()
    my_story_index = -1
    for i, s in enumerate(story_all):
        if s.user.id not in seen_users:
            unique_stories.append({'story': s, 'index': i})
            seen_users.add(s.user.id)
            if s.user == uid:
                my_story_index = i

    # Get IDs of posts liked by current user
    liked_posts = Like_Unlike.objects.filter(user_fk=uid).values_list('post_fk_id', flat=True)

    context = {
        'uid' : uid,
        'post_all' : post_all,
        'story_all' : story_all,
        'unique_stories' : unique_stories,
        'my_story_index' : my_story_index,
        'liked_posts': liked_posts,
    }
    return render(request,"myapp/home.html",context)

@checkLoggin
def logout(request):
    del request.session['email']
    return redirect("login")

@checkLoggin
def edit_profile(request):
    uid = request.uid 
    if request.POST:
        username = request.POST['username']
        name = request.POST['name']
        bio = request.POST['bio']
        description = request.POST['description']
        website = request.POST['website']

        uid = InstaUser.objects.get(email = request.session['email'])
        uid.username = username
        uid.name = name 
        uid.bio = bio
        uid.description = description
        uid.link = website

        if 'profile_pic' in request.FILES:
            uid.profile_pic = request.FILES['profile_pic']
        
        uid.save()
        return redirect("profile")
    return render(request,"myapp/edit_profile.html",{'uid':uid})

@checkLoggin
def create_post(request):
    uid = request.uid 
    if request.POST:
        caption = request.POST['caption']
        location = request.POST['location']
        image = request.FILES['image']

        InstaPost.objects.create(user = uid,
                                 image = image,
                                 caption = caption,
                                 location = location)
        return redirect("home")
    
    return render(request,"myapp/create_post.html",{'uid':uid})

@checkLoggin
def profile(request):
    uid = request.uid
    mypost = InstaPost.objects.filter(user=uid).order_by('-created_at')
    
    followers_count = Follow.objects.filter(following_person=uid).count()
    following_count = Follow.objects.filter(following=uid).count()

    # Get IDs of posts liked by current user
    liked_posts = Like_Unlike.objects.filter(user_fk=uid).values_list('post_fk_id', flat=True)

    context = {
        'uid' : uid,
        'mypost' : mypost,
        'followers_count': followers_count,
        'following_count': following_count,
        'liked_posts': liked_posts,
    }
    return render(request, "myapp/profile.html", context)

@checkLoggin
def following(request):
    uid = request.uid
    users = InstaUser.objects.exclude(username = uid.username)

    # my_following =Follow.objects.filter(following = uid).values_list('following_person_id',flat=True)
    my_following = Follow.objects.filter(following = uid)
    context = {
        'users' : users,
        'my_following' : my_following,
    }

    query = request.GET.get("q")

    if query:
        my_following = my_following.filter(
            Q(following_person__username__icontains = query) |
            Q(following_person__name__icontains = query)

        )
    return render(request,"myapp/following.html",context)

@checkLoggin
def follow_unfollow(request,pk):
    uid = request.uid
    target_user = InstaUser.objects.get(id=pk)
    follow_person = Follow.objects.filter(
                following=uid,
                following_person = target_user).first()
    
    if follow_person:
        follow_person.delete()
    else:
        Follow.objects.create(
            following = uid,
            following_person = target_user,
        )
        Notifications.objects.create(
            sender = uid,
            receiver = target_user,
            message = "started following u ",
            notification_type = "follow"
        )
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('following') 


@checkLoggin
def followers(request):
    
    uid = request.uid

    # user_id = Follow.objects.filter(id=uid)
    follow_list = Follow.objects.filter(following_person=uid)
    following_id = Follow.objects.filter(following=uid).values_list('following_person_id', flat=True)
    my_following = Follow.objects.filter(following=uid).values_list("following_person",flat=True)
    context = {
        'uid' : uid,
        'follow_list': follow_list,
        'following_id': following_id,
        'my_following' : my_following,
    }

    return render(request, "myapp/followers.html",context)

@checkLoggin
def remove_followers(request,pk):
    uid = request.uid
    target_user_follower = Follow.objects.filter(following_id=pk, following_person=uid).delete()
     
    return redirect("followers")

@checkLoggin
def explore(request):
    uid = request.uid
    liked_posts = Like_Unlike.objects.filter(user_fk=uid).values_list('post_fk_id', flat=True)
    context = {
        'uid': uid,
        'post_all': InstaPost.objects.all(),
        'reels_all': InstaReels.objects.all(),
        'liked_posts': liked_posts,
    }
    return render(request, "myapp/explore.html", context)


@checkLoggin
def notifications(request):
    uid = request.uid

    all_noti = Notifications.objects.filter(receiver = uid).order_by('-created_at')
    # Mark all as read
    all_noti.filter(read_status=False).update(read_status=True)
    my_following = Follow.objects.filter(following=uid).values_list("following_person",flat=True)
    context = {
        'uid' : uid,
        'all_noti' : all_noti,
        'my_following' : my_following,
    }
    return render(request,"myapp/notifications.html",context)

@checkLoggin
def settings(request):
    return render(request,"myapp/settings.html")

@checkLoggin
def like_unlike(request,pk):
    uid = request.uid

    post_id = InstaPost.objects.get(id=pk)

    likes = Like_Unlike.objects.filter(user_fk = uid,post_fk=post_id).first()

    if likes:
        likes.delete() # remove entry from model
        # Delete notification when unliking
        Notifications.objects.filter(
            sender = uid,
            receiver = post_id.user,
            notification_type = "like",
            post_fk = post_id
        ).delete()
    else:
        
        Like_Unlike.objects.create(user_fk = uid,post_fk=post_id)

        if post_id.user != uid:
            Notifications.objects.create(
                sender = uid,
                receiver = post_id.user,
                message = "Liked Your Post",
                notification_type = "like",
                post_fk = post_id,
            )

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect("home")



@checkLoggin
def upload_reel(request):
    uid = request.uid
    if request.POST:
        video = request.FILES['video']
        caption = request.POST['caption']
        location = request.POST['location']

        InstaReels.objects.create(
                user = uid,
                video = video,
                caption = caption,
                location = location
                )
        
        return redirect("home")
    return render(request,"myapp/upload_reel.html", {'uid': uid})

@checkLoggin
def reels(request):
    uid = request.uid
    all_reel = InstaReels.objects.all()
    context = {
        'uid' : uid,
        'all_reel' : all_reel
    }

    return render(request,"myapp/reels.html",context)


@checkLoggin
def create_story(request):
    uid = request.uid
    if request.POST:
        image = request.FILES['image']
        caption = request.POST['caption']
        video = request.POST['video']
        duration = request.POST['duration']
        audience = request.POST['audience']

        istory = InstaStory.objects.create(
            user = uid,
            image = image,
            caption = caption,
            video = video,
            duration = duration,
            audience = audience,
        )

        if "music" in request.FILES:
            istory.music = request.POST['music']

        istory.save()
        
    context = {
        'uid' : uid,
    }
    return render(request,"myapp/create_story.html",context)


@checkLoggin
def view_story(request):
    uid = request.uid
    my_following_users = Follow.objects.filter(following=uid).values_list("following_person", flat=True)
    users = list(my_following_users) + [uid.id]
    stories = InstaStory.objects.filter(
        user__in=users,
        expired_at__gt=timezone.now()
    ).order_by('user', '-created_at')

    context = {
        'stories': stories,
    }
    return render(request, "myapp/view_story.html", context)


def forgot_password(request):
    if request.POST:
        email = request.POST['email']
        try:
            uid=InstaUser.objects.get(email = email)
            if uid:
                otp = random.randint(1111,9999)
                uid.otp = otp
                uid.save()
                myCustomMail("forgot_password","mail",email,{'otp' : otp})
                context = {
                    'email' : email
                }
                print("----->>",email)

                return render(request,"myapp/verify_otp.html",context)

        except Exception as e:
            print("-----------> e",e)
            context = {
                'e_msg' : 'User donot exists !! '
            }
            return render(request,"myapp/forgot_password.html",context)
            
    else:
        return render(request,"myapp/forgot_password.html")




def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if 'otp' in request.POST:
            otp = request.POST.get('otp')
            try:
                uid = InstaUser.objects.get(email=email)
                if str(uid.otp) == otp:
                    return render(request, "myapp/reset_password.html", {'email': email})
                else:
                    return render(request, "myapp/verify_otp.html", {'email': email, 'e_msg': 'Invalid OTP'})
            except Exception:
                return redirect("forgot_password")
                
        elif 'password' in request.POST:
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                try:
                    uid = InstaUser.objects.get(email=email)
                    # uid.password = make_password(password)
                    uid.save()
                    return redirect("login")
                except Exception:
                    return redirect("forgot_password")
            else:
                return render(request, "myapp/reset_password.html", {'email': email, 'e_msg': 'Passwords do not match'})
                
    return render(request, "myapp/reset_password.html")

@checkLoggin
def messages(request,pk=None):
    uid = request.uid
    sender = InstaUser.objects.get(id = uid.id)
    receiver = None
    messages = None
    following_list = Follow.objects.filter(following = sender)

    following_users = [f.following_person for f in following_list]

    if pk:
        receiver = InstaUser.objects.get(id=pk)

        conversation_room = get_or_create_chatRoom(sender,receiver)
        messages = Messages.objects.filter(chat_room = conversation_room).order_by('created_at')
    context = {
        'uid' : uid,
        'sender'  : sender,
        'following_users'  : following_users,
        'receiver'  : receiver,
        'messages' : messages,
    }
    return render(request,"myapp/messages.html",context)


@checkLoggin
def send_message(request, pk):
    if request.method == "POST":
        uid = request.uid
        receiver = InstaUser.objects.get(id=pk)
        text_mssg = request.POST.get('text_mssg')
        
        conversation_room = get_or_create_chatRoom(uid, receiver)
        
        Messages.objects.create(
            chat_room=conversation_room,
            sender=uid,
            text_mssg=text_mssg
        )
        
        return redirect('messages', pk=pk)
    return redirect('messages')

@checkLoggin
def add_comment(request, pk):
    post = InstaPost.objects.get(id=pk)
    text = request.POST.get('comment_text')
    
    # Create the comment
    Comment.objects.create(user=request.uid, post=post, comment_text=text)
    
    # Create notification
    if post.user != request.uid:
        Notifications.objects.create(sender=request.uid, receiver=post.user, message="commented on your post", notification_type="comment", post_fk=post)
    
    return redirect('home')

@checkLoggin
def add_reel_comment(request, pk):
    reel = InstaReels.objects.get(id=pk)
    text = request.POST.get('comment_text')
    
    # Create the comment
    Comment.objects.create(user=request.uid, reel=reel, comment_text=text)
    
    # Create notification
    if reel.user != request.uid:
        Notifications.objects.create(sender=request.uid, receiver=reel.user, message="commented on your reel", notification_type="comment", reel_fk=reel)
    
    return redirect('reels')