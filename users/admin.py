from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# admin.site.register(User)

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('login_id', 'password')}),
        ('Personal info', {'fields': ('nickname', 'profile_photo', 'email', 'birthday')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login_id', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('login_id', 'nickname', 'is_active', 'is_staff')
    search_fields = ('login_id', 'nickname')
    ordering = ('login_id',)