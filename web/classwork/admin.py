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


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Session, SessiontAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register((ClassOffer, Location))
