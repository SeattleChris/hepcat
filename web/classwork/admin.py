from django.contrib import admin
# from django.db import models
from .models import Subject, Session, ClassOffer, Location

# Register your models here.


class SubjectAdmin(admin.ModelAdmin):
    """
    """
    model = Subject

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)

    #     return queryset

# class ProfileAdmin(admin.ModelAdmin):
#     model = Profile
#     list_display = ['__str__', 'username', 'highest_subject', 'level']
#     list_display_links = ('__str__', 'username')


class SessiontAdmin(admin.ModelAdmin):
    """
    """
    model = Session
    ordering = ('expire_date',)

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)

    #     return queryset


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Session, SessiontAdmin)
admin.site.register((ClassOffer, Location))
