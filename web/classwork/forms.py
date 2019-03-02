from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import Subject, Session, ClassOffer, Profile, Payment, Registration
# from .views import decide_session
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from django.contrib.auth import get_user_model
from datetime import datetime


def decide_session(sess=None, display_date=None):
    """ Typically we want to see the current session (returned if no params set)
        Sometimes we want to see a future sesion.
        Used by many views, generally those that need a list of ClassOffers
        that a user can view, sign up for, get a check-in sheet, pay for, etc.
    """
    sess_data = []
    # TODO: Deal with appropriate date input data and test it
    if sess is None:
        target = display_date or datetime.now()
        sess_data = Session.objects.filter(publish_date__lte=target, expire_date__gte=target)
    else:
        if display_date:
            raise SyntaxError("You can't filter by both Session and Date")
        if sess == 'all':
            return Session.objects.all()
        if not isinstance(sess, list):
            sess = [].append(sess)
        try:
            sess_data = Session.objects.filter(name__in=sess)
        except TypeError:
            sess_data = []
    print(sess_data)
    return sess_data  # a list of Session records, even if only 0-1 session

# class SignUpForm(UserCreationForm):
#     """ Building on top of the defaul UserCreationForm, we'll make a user
#         creation form
#     """

#     first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
#     last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
#     email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

#     class Meta:
#         model = get_user_model()
#         fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


#     # end of class SignUpForm


class SubjectForm(forms.ModelForm):
    """ Will generate a form for input on whichever fields we include.
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


User = get_user_model()


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    # end class UserForm


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile  # 1-to-1 with users.UserHC, also has .taken for classoffers
        fields = ['taken', ]

    # end class ProfileForm


class RegisterFriendForm(forms.ModelForm):
    """ If a user indicates that the student and the paying person are not the
        same, then this view will be called, while taking in the data they
        already entered.

        Perhaps this is not needed due to PaymentManager we made.
    """
    sess = decide_session()
    class_choices = ClassOffer.objects.filter(session__in=sess)
    # TODO: Change to CheckboxSelectMultiple and make sure it works
    first_name = forms.CharField(max_length=User._meta.get_field('first_name').max_length)
    last_name = forms.CharField(max_length=User._meta.get_field('last_name').max_length)
    email = forms.CharField(max_length=User._meta.get_field('email').max_length, widget=forms.EmailInput())
    # password = forms.CharField(min_length=6, max_length=16, widget=forms.PasswordInput())
    class_selected = forms.ModelMultipleChoiceField(queryset=class_choices)

    class Meta:
        model = Payment
        fields = [
            'billing_first_name',
            'billing_last_name',
            'billing_email',
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_postcode',
            ]


class RegisterForm(forms.ModelForm):
    """ This is where exisiting and even new users/students can sign up for
        a ClassOffer
    """
    # TODO: Create the workflow for when (if) the user wants to fill out the
    # registeration form for someone else,

    # Find the acceptable ClassOffers to show
    sess = decide_session()
    class_choices = ClassOffer.objects.filter(session__in=sess)

    class Meta:
        model = Payment
        fields = (
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_postcode',
        )

    # TODO: Change to CheckboxSelectMultiple and make sure it works
    first_name = forms.CharField(max_length=User._meta.get_field('first_name').max_length)
    last_name = forms.CharField(max_length=User._meta.get_field('last_name').max_length)
    email = forms.CharField(max_length=User._meta.get_field('email').max_length, widget=forms.EmailInput())
    # password = forms.CharField(min_length=6, max_length=16, widget=forms.PasswordInput())
    class_selected = forms.ModelMultipleChoiceField(queryset=class_choices)
    paid_by_other = forms.BooleanField(required=False)

    def clean(self):
        print('======== RegisterForm.clean =========')
        cleaned_data = super().clean()
        # there is no user inside the cleaned_data
        user = self.initial['user']  # TODO: Test when user login changes after form load
        if cleaned_data.get('paid_by_other'):
            # We need to now get the billing info for user who is paying
            # Assign the logged in user name & email to paid_by
            paid_by = Profile.objects.get(user=user)
            cleaned_data['paid_by'] = paid_by
            # paid_by may have given the same email for friend user:
            #   - maybe friend is an existing user (who has a diff email)
            #   - maybe friend is an existing user who also has that email
            #   - maybe friend is a brand new user, and we use same email
            # paid_by may have given an email different from their own:
            #   -  maybe the email is a typo/incorrect for existing friend user
            #   -  maybe email is friend user who exists w/ that email
            #   -  maybe email is friend user that needs to be created

            # if email does not match paid_by.email then we know the other user
            input_email = cleaned_data.get('email')
            first_name = cleaned_data.get('first_name')
            last_name = cleaned_data.get('last_name')
            if input_email is None:
                raise forms.ValidationError("Email is required")
            if first_name is None:
                raise forms.ValidationError("First Name is required")
            if last_name is None:
                raise forms.ValidationError("Last Name is required")
            # TODO: Above 3 could/should be done in respective clean_<field>
            possible_friends = User.objects.filter(email=input_email).exclude(id=user.id)
            uses_email_username = False if user.email == input_email or len(possible_friends) > 1 else True
            friend = possible_friends[0] if len(possible_friends) == 1 else None
            # if len(possible_friends) == 0:
            #     possible_friends = []
            if not friend:  # could be none in list, could have matching emails, could be many to choose from
                friend = User.objects.find_or_create_by_name(
                    first_name=first_name,
                    last_name=last_name,
                    email=input_email,
                    uses_email_username=uses_email_username,
                    is_student=True,
                    possible_users=possible_friends
                    )
                # if that user needed to be created, a decorator will create the profile
            else:
                print('friend found without using find_or_create_by_name')
            user = friend
        cleaned_data['student'] = Profile.objects.get(user=user)
        return cleaned_data

    def save(self, commit=True):
        print('======== Inside RegisterForm ===========')
        # student = self.cleaned_data.get('student')
        # print(f'student: {student}')
        # paid_by = self.cleaned_data.get('paid_by')
        # print(f'paid_by: {paid_by}')
        # print('======== Cleaned Data =================')
        # for ea in self.cleaned_data:
        #     print(ea)
        # TODO: If billing address info added to user Profile, let
        # Payment.objects.classRegister get that info from student (profile)
        # TODO: we could create a new dict with items starting with 'billing'
        # then pass that instead of each billing item below.
        # however neither approach needed if we put billing info
        # into the user Profile.
        payment = Payment.objects.classRegister(
            register=self.cleaned_data['class_selected'],
            student=self.cleaned_data['student'],
            paid_by=self.cleaned_data.get('paid_by'),
            billing_address_1=self.cleaned_data['billing_address_1'],
            billing_address_2=self.cleaned_data['billing_address_2'],
            billing_city=self.cleaned_data['billing_city'],
            billing_postcode=self.cleaned_data['billing_postcode'],
            )
        # We can not use objects.bulk_create due to Many-to-Many relationships
        for each in self.cleaned_data['class_selected']:
            print(each)
            Registration.objects.create(
                student=self.cleaned_data['student'],
                classoffer=each,
                payment=payment
                )
            print('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-')
        return payment

    # end class RegisterForm


class PaymentForm(forms.ModelForm):
    """ This is where a user inputs their payment data
        and it is processed.
    """

    class Meta:
        model = Payment
        fields = [
            'billing_first_name',
            'billing_last_name',
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_postcode',
            ]

