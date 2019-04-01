from django import forms
from .models import ClassOffer, Profile, Payment, Registration, Session
# from django.urls import reverse_lazy
# from django.shortcuts import render
from datetime import datetime
# TODO: should we be using datetime.datetime or datetime.today ?
from django.contrib.auth import get_user_model
User = get_user_model()


def decide_session(sess=None, display_date=None):
    """ Typically we want to see the current session (returned if no params set)
        Sometimes we want to see a future sesion.
        Used by many views, generally those that need a list of ClassOffers
        that a user can view, sign up for, get a check-in sheet, pay for, etc.
    """
    print('======= forms function - decide_session ==========')
    sess_data = []
    # TODO: Test alternative data input. Default happy path is working.
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


class RegisterForm(forms.ModelForm):
    """ This is where exisiting and even new users/students can sign up for
        a ClassOffer
    """
    # TODO: Create the workflow for when (if) the user wants to fill out the
    # registeration form for someone else,

    # Find the acceptable ClassOffers to show
    class_choices = ClassOffer.objects.filter(session__in=decide_session())
    user_answers = (('', 'Please Select an Answer'), ('T', 'This is my first'), ('F', 'I am a returning student'),)
    # TODO: Change to CheckboxSelectMultiple and make sure it works

    new_user = forms.ChoiceField(label='Have you had classes with us before?', choices=(user_answers))
    first_name = forms.CharField(max_length=User._meta.get_field('first_name').max_length)
    last_name = forms.CharField(max_length=User._meta.get_field('last_name').max_length)
    email = forms.CharField(max_length=User._meta.get_field('email').max_length, widget=forms.EmailInput())
    # password = forms.CharField(min_length=6, max_length=16, widget=forms.PasswordInput())
    class_selected = forms.ModelMultipleChoiceField(queryset=class_choices)
    paid_by_other = forms.BooleanField(required=False)
    new_fields = ['new_user', 'first_name', 'last_name', 'email', 'class_selected', 'paid_by_other']

    class Meta:
        model = Payment
        fields = (
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_postcode',
        )

    field_order = [*new_fields, *Meta.fields]
    # Cleaning data is done by:
    # 1) Field.clean() which will populate cleaned_data, and has 3 parts:
    #     a) to_python() to coerce datatype or raise ValidationError if impossible
    #     b) validate() field-specific validation that is not suitable for a validator
    #     c) run_validators() runs all validators and aggregates into single ValidationError
    # 2) clean_<fieldname>() Takes no params, must return the cleaned value even if unchanged
    # 3) Form.clean() where we can deal with cross-field validations.

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name is None:
            raise forms.ValidationError("First Name is required")
        value = first_name.capitalize()
        print(f'Modified first_name: "{value}"')
        return value

    def clean_last_name(self):
        value = self.cleaned_data.get('last_name')
        print('unmodified last_name:', value)
        if value is None:
            raise forms.ValidationError("Last Name is required")
        if value.isupper() or value.islower():
            # If they gave all caps, or all lower, assume this is not desired.
            print('Modified Last Name: ', value.capitalize())
            return value.capitalize()
        # However, some names have capitols in the middle, so leave unmodified.
        return value

    def clean_email(self):
        email = self.cleaned_data.get('email')
        print('unmodified email:', email)
        if email is None:
            raise forms.ValidationError("Email is required")
        # TODO: We could/should use an external email validator that uses our
        # desired casefold method. Technically capitols are allowed in emails,
        # but in practice almost everywhere makes them case-insensitive.
        # We are deciding to force all emails to lowercase (using casefold).
        # Which could be an error if a user does in fact require uppercase.
        return email.casefold()

    def clean(self):
        print('======== RegisterForm.clean =========')
        cleaned_data = super().clean()
        input_email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        new_user = cleaned_data.get('new_user') == 'T'
        print(f'new user: {new_user}')
        # there is no user inside the cleaned_data under any conditions
        user = self.initial['user']  # TODO: Test when user login changes after form load
        if user.is_anonymous:  # direct to login or create a new user account
            if new_user:
                # They say they are new, but we should check so we don't have collisions
                # Look by email
                same_email = User.objects.filter(email=input_email)
                uses_email_username = False if len(same_email) > 0 else True
                if len(same_email) > 0:
                    print('That email is already assigned to a user')
                    found = same_email.filter(first_name=first_name, last_name=last_name)
                    if len(found) > 0:
                        print('We found user account with that name and email')
                        raise forms.ValidationError('We found a user account with your name and email. Try the login link, or resubmit the form and select you are a returning student')
                        # If user was found, then we should have them login
                        # TODO: send user to login credentials, keep track of data they have given
                    # TODO: Create a system to deal with matches
                    # TODO: Either pass above queries to that function, or use .count() above.
                else:
                    print('No other user has that email')
                same_name = User.objects.filter(first_name=first_name, last_name=last_name).count()
                if same_name > 0:
                    print('We found user(s) with that same name')
                    # TODO: Create a system to deal with matches
                    # raise forms.ValidationError('Are you sure you have not had classes with us? We have someone with that name already in our records. If this is you, either login or select you are a returning student.')
                else:
                    print('No user with that name yet')
                user = User.objects.create_user(
                    email=input_email,
                    first_name=first_name,
                    last_name=last_name,
                    uses_email_username=uses_email_username,
                    )
            else:  # new_user is False
                # User says they have an account, we should use that account
                print('User says they are returning. They should login!')
                # for ea in dir(self):
                #     print(ea)
                query_user = User.objects.filter(email=input_email, first_name=first_name, last_name=last_name)
                if len(query_user) > 1:
                    print('MULTIPLE users with that email & name. We are using the first one.')
                user = query_user[0] if len(query_user) > 0 else None
                # TODO: Above allows anyone to add the user to the class. Perhaps we should force a login.
                if not user:
                    raise forms.ValidationError("We did not find your user account with your name and email address. Try the login link. If that does not work, select that you are a new student and we can fix it later.")
            # user = User.objects.find_or_create_for_anon(email=input_email, first_name=first_name, last_name=last_name)
            # TODO: What if a non-user is paying for a friend (established or new user)
        print(f'user before paid_by_other check {user}')
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
        print(f'user as used for student profile {user}')
        cleaned_data['student'] = Profile.objects.get(user=user)
        print(f"student profile: {cleaned_data['student']}")
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
