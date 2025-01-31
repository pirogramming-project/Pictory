from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Frame)
admin.site.register(Photo)
admin.site.register(Sticker)
admin.site.register(Diary)
admin.site.register(Tag)
admin.site.register(User_Tag)
admin.site.register(Like)
admin.site.register(Comment)