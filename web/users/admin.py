from django.contrib import admin
from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserHC, Staff, Student
# Register your models here.


class StaffInline(admin.StackedInline):
    """ How to add a profile to a user model according to:
        https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
    """
    model = Staff
    can_delete = False
    verbose_name_plural = 'staff'


class StudentInline(admin.StackedInline):
    """ How to add a profile to a user model according to:
        https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
    """
    model = Student
    can_delete = False


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = get_user_model()  # UserHC
    list_display = ['first_name', 'last_name', 'uses_email_username', 'username', 'is_student', 'is_teacher', 'is_admin']
    empty_value_display = '-empty-'
    inlines = (StaffInline, StudentInline,)

    # fields = ('first_name', 'last_name', 'uses_email_username', 'username', 'email', )


admin.site.register(UserHC, CustomUserAdmin)
admin.site.register((Staff, Student))
