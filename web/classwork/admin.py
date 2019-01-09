from django.contrib import admin
from .models import Subject, Session, ClassOffer, Location

# Register your models here.

class SubjectAdmin(admin.ModelAdmin):
    """
    """

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset


admin.site.register(Subject, SubjectAdmin)
admin.site.register((Session, ClassOffer, Location))
