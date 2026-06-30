from django.contrib import admin
from .models import * 
# Register your models here.
class InstaUserAdmin(admin.ModelAdmin):
    list_display = ["id","username","email","created_at"]
    search_fields = ["username","email"]
    list_display_links = ["username"]
    list_per_page = 10  
    list_filter = ["created_at"]
    # list_order_by_desc = ["created_at"] # This is usually handled in ordering

admin.site.register(InstaUser,InstaUserAdmin)

class InstaPostAdmin(admin.ModelAdmin):
    list_display = ["id","user","caption","location","created_at"]
    search_fields = ["caption","location"]
    list_filter = ["created_at"]

admin.site.register(InstaPost,InstaPostAdmin)

admin.site.register(Follow)
admin.site.register(Notifications)
admin.site.register(Like_Unlike)
admin.site.register(InstaReels)
admin.site.register(InstaStory)
admin.site.register(ChatRoom)
admin.site.register(Messages)
