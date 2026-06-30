from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q
from .models import * 

def myCustomMail(subject,template,to,context):
    
    template_str = 'myapp/'+ template+'.html'
    html_message = render_to_string(template_str, {'data': context})
    plain_message = strip_tags(html_message)
    from_email = 'maheksavaliya3004@gmail.com'
    send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def get_or_create_chatRoom(user1,user2):
    conversation = ChatRoom.objects.filter(
        Q(user1 = user1,user2 = user2) |
        Q(user1 = user2,user2 = user1)

    ).first()

    if conversation:
        return conversation
    
    return ChatRoom.objects.create(user1 = user1,user2 = user2)