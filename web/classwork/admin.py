from django.contrib import admin
# from django.db import models
from .models import Subject, Session, ClassOffer, Profile, Registration, Location

# Register your models here.


class SubjectAdmin(admin.ModelAdmin):
    """
    """
    model = Subject

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)

    #     return queryset


class SessiontAdmin(admin.ModelAdmin):
    """
    """
    model = Session
    ordering = ('expire_date',)

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)

    #     return queryset


class StudentClassInline(admin.TabularInline):
    model = Registration
    extra = 2


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ['__str__', 'username', 'highest_subject', 'level', 'beg_finished', 'l2_finished']
    list_display_links = ('__str__', 'username')
    filter_horizontal = ('taken',)
    ordering = ('date_modified', 'date_added',)
    inlines = (StudentClassInline, )


class RegistrationAdmin(admin.ModelAdmin):
    model = Registration
    list_display = ['first_name', 'last_name', 'credit', 'reg_class']
    list_display_links = ['first_name', 'last_name']
    list_filter = ('classoffer__session', 'classoffer__class_day')
    # TODO: add ability to only display the class_day that exist in qs
    # https://docs.djangoproject.com/en/2.1/ref/contrib/admin/ see list_filter
    # TODO: modify so by default it shows current session filter
    ordering = ('-classoffer__class_day', 'classoffer__start_time', 'student__user__first_name')

    # ordering = ('reg_class', )


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Session, SessiontAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register((ClassOffer, Location))
