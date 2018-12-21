from django.contrib import admin
from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserHC, Staff, Student
# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = UserHC
    list_display = ['first_name', 'last_name', 'uses_email_username', 'username', 'is_student', 'is_teacher', 'is_admin']
    # list_display = ['username', 'email', ]
    # fields = ('first_name', 'last_name', 'uses_email_username', 'username', 'email', )


admin.site.register(UserHC, CustomUserAdmin)
admin.site.register((Staff, Student))
# admin.site.register((CustomUserCreationForm, CustomUserChangeForm))
# admin.site.register((UserHC, CustomUserAdmin, CustomUserCreationForm, CustomUserChangeForm))
