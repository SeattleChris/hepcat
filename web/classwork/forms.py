from django import forms
from .models import Student, Payment, Registration, Notify  # , Staff, Session, ClassOffer
from django.utils.translation import gettext_lazy as _
# from django.urls import reverse_lazy
# from django.shortcuts import render
# TODO: should we be using datetime.datetime or datetime.today ?
from django.contrib.auth import get_user_model
from collections import abc
User = get_user_model()


class RegisterForm(forms.ModelForm):
    """ This is where existing and even new users/students can sign up for a ClassOffer """
    # TODO: Lookup formsets. See if we can make a form combining fields from User and from Payment models.
    # TODO: Create the workflow for when (if) the user wants to fill out the registration form for someone else.

    user_answers = (('', _('Please Select an Answer')),
                    ('T', _('This is my first')),
                    ('F', _('I am a returning student')),
                    )
    # payment_answers = (('F', 'Paid by the above student'), ('T', 'Paid by someone other than student listed above'))
    new_user = forms.ChoiceField(label=_('Have you had classes with us before?'), choices=(user_answers))
    first_name = forms.CharField(label=_('First Name'), max_length=User._meta.get_field('first_name').max_length)
    last_name = forms.CharField(label=_('Last Name'), max_length=User._meta.get_field('last_name').max_length)
    email = forms.CharField(max_length=User._meta.get_field('email').max_length, widget=forms.EmailInput())
    # password = forms.CharField(min_length=6, max_length=16, widget=forms.PasswordInput())
    # TODO: Change to CheckboxSelectMultiple and make sure it works
    class_selected = forms.ModelMultipleChoiceField(label=_('Choose your class(es)'), queryset=None)
    paid_by_other = forms.BooleanField(label=_('paid by a different person'), required=False)
    new_fields = ['new_user', 'first_name', 'last_name', 'email', 'class_selected', 'paid_by_other']

    class Meta:
        model = Payment
        fields = (
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_country_area',
            'billing_postcode',
        )
        labels = {
            'billing_address_1': _('Street Address (line 1)'),
            'billing_address_2': _('Street Address (continued)'),
            'billing_city': _('City'),
            'billing_country_area': _('State'),
            'billing_postcode': _('Zip'),
        }
        help_texts = {
            'billing_country_area': _('State, Territory, or Province'),
            'billing_postcode': _('Zip or Postal Code'),
        }

    field_order = [*new_fields, *Meta.fields]

    def __init__(self, *args, **kwargs):
        # print('========= RegistrationForm.__init__========================')
        class_choices = kwargs.pop('class_choices', None)
        # print(class_choices)
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['class_selected'].queryset = class_choices
        self.focus_first_usable_field(self.fields.values())

    def focus_first_usable_field(self, fields):
        """ Gives autofocus to the first non-hidden, non-disabled form field from the given iterable of form fields. """
        if not isinstance(fields, (list, tuple, abc.ValuesView)):
            raise TypeError(_("Expected an iterable of form fields. "))
        field_gen = (ea for ea in fields)
        first_field = next(field_gen)
        while first_field.disabled or (hasattr(first_field, 'is_hidden') and first_field.is_hidden):
            if 'autofocus' in first_field.widget.attrs:
                first_field.widget.attrs['autofocus'] = False
            first_field = next(field_gen)
        first_field.widget.attrs['autofocus'] = True
        return first_field

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
        return first_name.capitalize()

    def clean_last_name(self):
        value = self.cleaned_data.get('last_name')
        if value is None:
            raise forms.ValidationError("Last Name is required")
        if value.isupper() or value.islower():
            # If they gave all caps, or all lower, assume this is not desired.
            return value.capitalize()
        # However, some names have capitols in the middle, so leave unmodified.
        return value

    def clean_email(self):
        email = self.cleaned_data.get('email')
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
            if new_user:  # They say they are new, but we should check so we don't have collisions
                # Look by email
                same_email = User.objects.filter(email__iexact=input_email)
                if same_email.count():
                    # print('That email is already assigned to a user')
                    found = same_email.filter(first_name__iexact=first_name, last_name__iexact=last_name).count()
                    if found:
                        message = 'We found a user account with your name and email. '
                        # print(message)
                        message += 'Try the login link, or resubmit the form and select you are a returning student'
                        raise forms.ValidationError(_(message))
                        # If user was found, then we should have them login
                        # TODO: send user to login credentials, keep track of data they have given
                    # TODO: Create a system to deal with matches
                    # TODO: Either pass above queries to that function, or use .count() above.
                else:
                    print('No other user has that email')
                # Look by name
                same_name = User.objects.filter(first_name=first_name, last_name=last_name)
                if same_name.count():
                    print('We found user(s) with that same name')
                    message = "Are you sure you have not had classes with us? "
                    message += "We have someone with that name already in our records. "
                    message += "If this is you, either login or select you are a returning student. "
                    message += "If this is not you, please resubmit with either a variation of your name or include an "
                    # TODO: Create a system to deal with matching names, but are unique people
                    message += "extra symbol (such as '.' or '+') at the end of your name to confirm your input"
                    raise forms.ValidationError(_(message))
                else:
                    print('No user with that name yet')
                user = User.objects.create_user(
                    email=input_email,
                    first_name=first_name,
                    last_name=last_name,
                    )
            else:  # new_user is False; User says they have an account, we should use that account.
                print('User says they are returning. They should login!')
                query_user = User.objects.filter(email__iexact=input_email, first_name=first_name, last_name=last_name)
                user_count = query_user.count()
                if user_count > 1:
                    print('MULTIPLE users with that email & name. We are using the first one.')
                # TODO: Create Logic when more than one user has the same email, for now using first match.
                user = query_user.first() if user_count > 0 else None  # TODO: refactor to use get_one_or_none ?
                # TODO: Above allows anyone to add the user to the class. Perhaps we should force a login.
                if not user:
                    message = "We did not find your user account with your name and email address. "
                    message += "Try the login link. "
                    message += "If that does not work, select that you are a new student and we can fix it later. "
                    raise forms.ValidationError(_(message))
            # user = User.objects.find_or_create_for_anon(email=input_email, first_name=first_name, last_name=last_name)
            # TODO: What if a non-user is paying for a friend (established or new user)
        print(f'user before paid_by_other check {user}')
        if cleaned_data.get('paid_by_other'):
            # We need to now get the billing info for user who is paying
            # Assign the logged in user name & email to paid_by
            paid_by = Student.objects.filter(user=user).first()
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
            possible_friends = User.objects.filter(email__iexact=input_email).exclude(id=user.id)
            num_friends = possible_friends.count()
            username_not_email = True if user.email == input_email or num_friends > 1 else False
            friend = possible_friends.first() if num_friends == 1 else None
            if not friend:  # could be none in list, could have matching emails, could be many to choose from
                friend = User.objects.find_or_create_by_name(
                    first_name=first_name,
                    last_name=last_name,
                    email=input_email,
                    username_not_email=username_not_email,
                    is_student=True,
                    possible_users=possible_friends
                    )
                # if that user needed to be created, a decorator will create the profile
            else:
                print('friend found without using find_or_create_by_name')
            user = friend
        print(f'user as used for student profile {user}')
        cleaned_data['student'] = Student.objects.get(user=user)
        print(f"student profile: {cleaned_data['student']}")
        print(f"class selected: {cleaned_data['class_selected']}")
        return cleaned_data

    def save(self, commit=True):
        print('======== Inside RegisterForm.save ===========')
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
        class_selected = self.cleaned_data.get('class_selected')
        student = self.cleaned_data.get('student')  # Profile for the User taking the ClassOffer
        paid_by = self.cleaned_data.get('paid_by')  # Profile for the User paying for the ClassOffer
        # TODO: Send confirmation email here? Or maybe do so with a decorator after save?
        email = Notify.register(selected=class_selected, student=student, paid_by=paid_by)
        if email:
            print(f"Email was sent for register of {student} paid by {paid_by}")
        else:
            print(f"Email ERROR for registering {student}")
        # Create payment for all, then a Registration for each class they selected.
        payment = Payment.objects.classRegister(
            register=class_selected,
            student=student,
            paid_by=paid_by,
            billing_address_1=self.cleaned_data['billing_address_1'],
            billing_address_2=self.cleaned_data['billing_address_2'],
            billing_city=self.cleaned_data['billing_city'],
            billing_country_area=self.cleaned_data['billing_country_area'],
            billing_postcode=self.cleaned_data['billing_postcode'],
            )
        # We can not use objects.bulk_create due to Many-to-Many relationships
        for each in class_selected:
            print(each)
            Registration.objects.create(
                student=student,
                classoffer=each,
                payment=payment
                )
            print('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-')
        return payment

    # end class RegisterForm


class PaymentForm(forms.ModelForm):
    """ This is where a user inputs their payment data and it is processed. """

    class Meta:
        model = Payment
        fields = [
            'billing_first_name',
            'billing_last_name',
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_country_area',
            'billing_postcode',
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.focus_first_usable_field(self.fields.values())

    def focus_first_usable_field(self, fields):
        """ Gives autofocus to the first non-hidden, non-disabled form field from the given iterable of form fields. """
        if not isinstance(fields, (list, tuple, abc.ValuesView)):
            raise TypeError(_("Expected an iterable of form fields. "))
        field_gen = (ea for ea in fields)
        first_field = next(field_gen)
        while first_field.disabled or (hasattr(first_field, 'is_hidden') and first_field.is_hidden):
            if 'autofocus' in first_field.widget.attrs:
                first_field.widget.attrs['autofocus'] = False
            first_field = next(field_gen)
        first_field.widget.attrs['autofocus'] = True
        return first_field
