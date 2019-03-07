from django.contrib import admin
from django.forms import Textarea
from django.db import models
from .models import Resource, Subject, Session, ClassOffer, Profile, Registration, Location
# from django.utils.functional import curry

# Register your models here.


class ResourceInline(admin.StackedInline):
    model = Resource
    extra = 5

    # prepopulated_fields does not allow me to set defaults or initial
    # autocomplete does not allow me to set defaults or initial
    # formfield_overrides ... uh, I think that only changes widgets?
    # fields = ('related_type', 'subject', 'classoffer', 'user_type', 'avail', 'content_type', 'filepath', )
    # exclude = ('classoffer', )
    # get_changeform_initial_data is not for this context.

    fieldsets = (
        (None, {
            'fields': (('user_type', 'avail'), ('content_type', 'filepath',)),
        }),
        (None, {
            # 'classes': ('collapse',),
            'fields': ('description',),
        }),
        # ('To Hide', {
        #     'fields': ('related_type', 'subject', 'classoffer', ),
        #     # 'classes': ('hidden', ),
        # }),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'cols': 60, 'rows': 2})},
    }

    # def get_changeform_initial_data(request):
    #     initial = {}
    #     print('====== ResourceInline . get_changeform_initial_data =====')
    #     return initial

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        print('========== ResourceInline.get_formset ================')
        print(self)
        for ea in dir(self):
            print(ea)
        # print(self.parent_model)
        print('----------- Obj -----------')
        print(obj)
        # for ea in dir(obj):
        #     print(ea)
        related, subject, classoffer = '', None, None
        if isinstance(obj, Subject):
            related = 'Subject'
            subject = obj
            classoffer = None
            self.exclude = ('related_type', 'classoffer',)
        elif isinstance(obj, ClassOffer):
            related = 'ClassOffer'
            subject = None
            classoffer = obj
            self.exclude = ('subject',)
        else:
            related = 'Other'
            subject = None
            classoffer = None
            self.exclude = ('subject', 'classoffer', )
        print(f'{related}, subj: {subject}, co: {classoffer}')
        # initial.append({
        #     'related_type': related,
        #     'subject': subject,
        #     'classoffer': classoffer,
        # })
        formset = super(ResourceInline, self).get_formset(request, obj, **kwargs)
        # formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class SubjectAdmin(admin.ModelAdmin):
    """
    """
    model = Subject

    list_display = ('__str__', 'title', 'level', 'version', )
    list_display_links = ('__str__', 'title')
    inlines = (ResourceInline, )

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)

    #     return queryset


class ClassOfferAdmin(admin.ModelAdmin):
    """
    """
    model = Subject

    list_display = ('__str__', 'subject', 'session',)
    # ('subject', 'session', 'teachers', 'class_day', 'start_time',)
    list_display_links = ('__str__',)
    inlines = (ResourceInline, )

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
    list_display = ['first_name', 'last_name', 'credit', 'reg_class', 'paid']
    list_display_links = ['first_name', 'last_name']
    list_filter = ('classoffer__session', 'classoffer__class_day')
    # TODO: add ability to only display the class_day that exist in qs
    # https://docs.djangoproject.com/en/2.1/ref/contrib/admin/ see list_filter
    # TODO: modify so by default it shows current session filter
    ordering = ('-classoffer__class_day', 'classoffer__start_time', 'student__user__first_name')

    # ordering = ('reg_class', )


admin.site.register(Subject, SubjectAdmin)
admin.site.register(ClassOffer, ClassOfferAdmin)
admin.site.register(Session, SessiontAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register((Location))
