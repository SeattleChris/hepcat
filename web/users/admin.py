from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserHC, Staff, Student, Profile
# Register your models here.


class StaffInline(admin.StackedInline):
    """ How to add a profile to a user model according to:
        https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
    """
    model = Staff
    can_delete = False
    verbose_name_plural = 'staff profile'


class StudentInline(admin.StackedInline):
    """ How to add a profile to a user model according to:
        https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
    """
    model = Student
    can_delete = False
    verbose_name_plural = 'student profile'


class ProfileInline(admin.StackedInline):
    """ How to add a profile to a user model according to:
        https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'user profile'


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = get_user_model()  # UserHC
    list_display = ['first_name', 'last_name', 'uses_email_username', 'username', 'is_student', 'is_teacher', 'is_admin', 'password']
    list_display_links = ('first_name', 'last_name', 'username')
    ordering = ('first_name',)

    # search_fields = ('first_name', 'last_name', 'email')
    empty_value_display = '-empty-'
    # TODO: Can we change to show only 1 and the correct profile inline?
    # inlines = (StaffInline, StudentInline,)
    inlines = (ProfileInline,)

    # fields = ('first_name', 'last_name', 'uses_email_username', 'username', 'email', )


admin.site.register(UserHC, CustomUserAdmin)
admin.site.register((Staff, Student, Profile))
