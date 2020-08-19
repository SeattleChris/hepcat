from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import UserHC, StaffUser, StudentUser
# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = UserHC
    list_display = ('first_name', 'last_name', 'username', 'is_student', 'is_teacher', 'is_admin', 'is_active', 'grp', 'perm', )
    list_display_links = ('first_name', 'last_name', 'username', )
    list_filter = ('is_student', 'is_teacher', 'is_admin', 'is_staff', 'is_active', )  # , 'is_superuser',
    ordering = ('first_name', )
    fieldsets = (
        (None, {'fields': (('email', 'uses_email_username'), 'password', ('is_student', 'is_teacher', 'is_admin'),), }),
        (_('Name info'), {'fields': (('first_name', 'last_name'), ), }),
        (_('Address Info'), {
            'classes': ('collapse', ),
            'fields': (
                'billing_address_1', 'billing_address_2',
                ('billing_city', 'billing_country_area', 'billing_postcode', ),
                'billing_country_code',
            ),
        }),
        (_('Activity Dates'), {'classes': ('collapse', ), 'fields': (('last_login', 'date_joined'), ), }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                ('first_name', 'last_name'),
                ('email', 'uses_email_username'),
                ('is_student', 'is_teacher', 'is_admin'),
                ('password1', 'password2'), ),
        }),
        (_('Address Info'), {
            # 'classes': ('collapse', ),
            'fields': (
                'billing_address_1', 'billing_address_2',
                ('billing_city', 'billing_country_area', 'billing_postcode', ),
                'billing_country_code',
            ),
        }),
    )
    search_fields = ('first_name', 'last_name', 'email')
    empty_value_display = '-empty-'
    formfield_overrides = {  # attrs{'size': 'Num'} will actually be ~ 1.1*Num + 2
        models.CharField: {'widget': TextInput(attrs={'size': '15'})},
        models.EmailField: {'widget': TextInput(attrs={'size': '25'})},
    }
    formfield_attrs_overrides = {
        'email': {'maxlength': 191, },
        'billing_address_1': {'size': 20},
        'billing_address_2': {'size': 20},
    }

    def grp(self, obj): return ', '.join(str(ea) for ea in obj.groups.all())
    def perm(self, obj): return ', '.join(str(ea) for ea in obj.user_permissions.all())

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name, field in form.base_fields.items():
            if name in self.formfield_attrs_overrides:
                for key, value in self.formfield_attrs_overrides[name].items():
                    field.widget.attrs[key] = value
            if not self.formfield_attrs_overrides.get(name, {}).get('no_size_override', False):
                display_size = field.widget.attrs.get('size', float("inf"))  # Cannot use float("inf") as an int.
                input_size = field.widget.attrs.get('maxlength', None)
                if input_size:
                    field.widget.attrs['size'] = str(int(min(float(display_size), float(input_size))))
        return form

    # def get_formsets_with_inlines(self, request, obj=None):
    #     """ Return no inlines when obj is being created. Using super to use
    #         the default get_inline_instances, then filter so we return desired
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


class StaffUserAdmin(CustomUserAdmin):
    model = StaffUser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)


class StudentUserAdmin(CustomUserAdmin):
    model = StudentUser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_student=True)


# admin.site.register(UserHC, CustomUserAdmin)
admin.site.register(StaffUser, StaffUserAdmin)
admin.site.register(StudentUser, StudentUserAdmin)
