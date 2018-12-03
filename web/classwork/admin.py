from django.contrib import admin
from .models import Subject, Session, ClassOffer, Location

# Register your models here.
admin.site.register((Subject, Session, ClassOffer, Location))
