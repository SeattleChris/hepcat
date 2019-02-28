from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserHC  # Staff, Student, Profile
from django.utils.translation import gettext_lazy as _
# Register your models here.


# class StaffInline(admin.StackedInline):
#     """ How to add a profile to a user model according to:
#         https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
#     """
#     model = Staff
#     can_delete = False
#     verbose_name_plural = 'staff profile'


# class StudentInline(admin.StackedInline):
#     """ How to add a profile to a user model according to:
#         https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
#     """
#     model = Student
#     can_delete = False
#     verbose_name_plural = 'student profile'


# class ProfileInline(admin.StackedInline):
#     """ How to add a profile to a user model according to:
#         https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
#     """
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'user profile'


class CustomUserAdmin(UserAdmin):
    model = get_user_model()  # UserHC
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['first_name', 'last_name', 'uses_email_username', 'username', 'is_student', 'is_teacher', 'is_admin',]
    list_display_links = ('first_name', 'last_name', 'username')
    ordering = ('first_name',)
    fieldsets = (
        (None, {'fields': ('email', 'password', ('is_student', 'is_teacher', 'is_admin'), 'uses_email_username')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'is_student', 'is_teacher', 'is_admin', 'uses_email_username', 'password1', 'password2'),
        }),
    )
    # search_fields = ('first_name', 'last_name', 'email')
    empty_value_display = '-empty-'
    # TODO: Can we change to show only 1 and the correct profile inline?
    # inlines = (StaffInline, StudentInline, ProfileInline,)  # All three are just for testing
    # inlines = (StaffInline, StudentInline,)
    # inlines = (ProfileInline,)

    # def get_formsets_with_inlines(self, request, obj=None):
    #     """ Return no inlines when obj is being created. Using super to use
    #         the defaul get_inline_instances, then filter so we return desired
    #         inline based on user type.
    #     """
    #     if not obj:
    #         return []
    #     inline_list = self.get_inline_instances(request, obj)
    #     if not obj.is_teacher and not obj.is_admin:
    #         inline_list = [x for x in inline_list if not isinstance(x, StaffInline)]
    #     if not obj.is_student:
    #         inline_list = [x for x in inline_list if not isinstance(x, StudentInline)]
    #     for inline in inline_list:
    #         yield inline.get_formset(request, obj), inline

    # def get_inline_instances(self, request, obj=None):
    #     inline_list = super(CustomUserAdmin, self).get_inline_instances(request, obj)
    #     if not obj.is_teacher and not obj.is_admin:
    #         inline_list = [x for x in inline_list if not isinstance(x, StaffInline)]
    #     if not obj.is_student:
    #         inline_list = [x for x in inline_list if not isinstance(x, StudentInline)]
    #     return inline_list


admin.site.register(UserHC, CustomUserAdmin)
# admin.site.register((Staff, Student, Profile))
# admin.site.register((Staff, Student))
