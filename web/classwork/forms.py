from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import Subject, Session, ClassOffer
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput


# class SignUpForm(UserCreationForm):
#     """ Building on top of the defaul UserCreationForm, we'll make a user
#         creation form
#     """

#     first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
#     last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
#     email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


#     # end of class SignUpForm


class SubjectForm(forms.ModelForm):
    """ Will generate a form for input on whichever fields we include.
        Using Transaction model, since we are adding a withdraw or deposit
    """
    class Meta:
        model = Subject
        fields = ['level', 'version', 'title', 'num_weeks', 'num_minutes', 'short_desc', 'description', 'syllabus', 'teacher_plan', 'image', 'video_wk1', 'email_wk1', 'video_wk2', 'email_wk2', 'video_wk3', 'email_wk3', 'video_wk4', 'email_wk4', 'video_wk5', 'email_wk5']


class SessionForm(forms.ModelForm):
    """ Used for the admin to create a session
    """
    class Meta:
        model = Session
        fields = ['name', 'num_weeks', 'key_day_date', 'max_day_shift', 'publish_date', 'expire_date']
        # https://github.com/monim67/django-bootstrap-datepicker-plus
        widgets = {
            'key_day_date': DatePickerInput(format='%m/%d%Y'),
            'publish_date': DatePickerInput(format='%m/%d%Y'),
            'expire_date': DatePickerInput(format='%m/%d%Y'),
        }

        # https://stackoverflow.com/questions/16356289/how-to-show-datepicker-calendar-on-datefield/16356818
        # widgets = {
        #     'key_day_date': forms.DateInput(attrs={'class': 'datepicker'}),
        #     'publish_date': forms.DateInput(attrs={'class': 'datepicker'}),
        #     'expire_date': forms.DateInput(attrs={'class': 'datepicker'}),
        #     }


class ClassOfferForm(forms.ModelForm):
    """ Used for the admin or privliged teacher to create a specific class.
        This will connect to the models for Subject, Session, Teachers, Location.
    """
    class Meta:
        model = ClassOffer
        fields = ['subject', 'session', 'teachers', 'class_day', 'start_time']
        # https://github.com/monim67/django-bootstrap-datepicker-plus
        widgets = {
            'start_time': TimePickerInput()
            # options={"stepping": 5}
        }
