from django.forms import ModelForm
from .models import Subject, Session


class SubjectForm(ModelForm):
    """ Will generate a form for input on whichever fields we include.
        Using Transaction model, since we are adding a withdraw or deposit
    """
    class Meta:
        model = Subject
        fields = ['level', 'version', 'title', 'num_weeks', 'num_minutes', 'short_desc', 'description', 'syllabus', 'teacher_plan', 'image', 'video_wk1', 'email_wk1', 'video_wk2', 'email_wk2', 'video_wk3', 'email_wk3', 'video_wk4', 'email_wk4', 'video_wk5', 'email_wk5']


class SessionForm(ModelForm):
    """ Used for the admin to create a session
    """
    class Meta:
        model = Session
        fields = ['name', 'num_weeks', 'key_day_date', 'max_day_shift', 'publish_date', 'expire_date']
