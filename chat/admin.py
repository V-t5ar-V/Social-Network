from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Chat)
admin.site.register(ChatMember)
admin.site.register(Message)
admin.site.register(StickerMessage)
admin.site.register(Sticker)
admin.site.register(Keyword)