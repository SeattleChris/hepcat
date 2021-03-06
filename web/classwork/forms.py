from django import forms
from django.core.exceptions import ValidationError  # NON_FIELD_ERRORS,
from django.contrib.auth import get_user_model
from django.forms.fields import FileField  # Field,
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget
from .models import Student, Payment, Registration, Notify  # , Staff, Session, ClassOffer
from users.mixins import FocusMixIn, AddressUsernameMixIn  # AddressMixIn,
# from django.urls import reverse_lazy
# from django.shortcuts import render
# TODO: should we be using datetime.datetime or datetime.today ?
User = get_user_model()


class RegisterForm(AddressUsernameMixIn, forms.ModelForm):
    """This is where existing and even new users/students can sign up for a ClassOffer """
    # TODO: Lookup formsets. See if we can make a form combining fields from User and from Payment models.

    user_answers = (('', _('Please Select an Answer')),
                    ('T', _('This is my first')),
                    ('F', _('I am a returning student')),
                    )
    # payment_answers = (('F', 'Paid by the above student'), ('T', 'Paid by someone other than student listed above'))
    new_user = forms.ChoiceField(label=_('Have you had classes with us before?'), choices=(user_answers))
    first_name = forms.CharField(label=_('First Name'), max_length=User._meta.get_field('first_name').max_length)
    last_name = forms.CharField(label=_('Last Name'), max_length=User._meta.get_field('last_name').max_length)
    email = forms.CharField(label=_('Email'), max_length=User._meta.get_field('email').max_length,
                            widget=forms.EmailInput())
    # TODO: Change to CheckboxSelectMultiple and make sure it works
    class_selected = forms.ModelMultipleChoiceField(label=_('Choose your class(es)'), queryset=None)
    paid_by_other = forms.BooleanField(label=_('paid by a different person'), required=False)
    new_fields = ['first_name', 'last_name', 'new_user', 'email', 'class_selected', 'paid_by_other']

    class Meta:
        model = Payment
        fields = (
            'billing_address_1',
            'billing_address_2',
            'billing_city',
            'billing_country_area',
            'billing_postcode',
            'billing_country_code',
        )
        labels = {
            'billing_address_1': _('Street Address'),
            'billing_address_2': _('Address (continued)'),
            'billing_city': _('City'),
            'billing_country_area': _('State'),
            'billing_postcode': _('Zipcode'),
            'billing_country_code': _('Country'),
        }
        widgets = {'billing_country_code': CountrySelectWidget()}  # Adds the flag image.

    field_order = [*new_fields, *Meta.fields]

    def __init__(self, *args, **kwargs):
        print("======================= classwork.RegisterForm.__init__ =================================")
        class_choices = kwargs.pop('class_choices', None)
        self.base_fields['class_selected'].queryset = class_choices
        super(RegisterForm, self).__init__(*args, **kwargs)
        print("--------------------- FINISH RegisterForm.__init__ --------------------")

    def clean_first_name(self):
        print('======== RegisterForm.clean_first_name =========')
        first_name = self.cleaned_data.get('first_name')
        return first_name.capitalize()

    def clean_last_name(self):
        print('======== RegisterForm.clean_last_name =========')
        value = self.cleaned_data.get('last_name')
        if value.isupper() or value.islower():  # Some names have mid-capitols, so assume mixed capitals are intended.
            return value.capitalize()  # Assume unintended if it was all caps, or all lowercase.
        return value

    def clean_email(self):
        print('======== RegisterForm.clean_email =========')
        email = self.cleaned_data.get('email')
        # We are using casefold() to lowercase, which may technically be incorrect for the user's email system.
        return email.casefold()

    def _clean_fields(self):
        # print('======== RegisterForm._clean_fields =========')
        # super()._clean_fields()
        print('======== Duplicate code as normal: RegisterForm._clean_fields =========')
        for name, field in self.fields.items():
            # The widget.value_from_datadict() can handle if it's data is split across several fields in self.data.
            if field.disabled:
                value = self.get_initial_for_field(field, name)
            else:
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, FileField):
                    initial = self.get_initial_for_field(field, name)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)

    def _clean_form(self):
        print('======== RegisterForm._clean_form =========****************')
        super()._clean_form()

    def full_clean(self):
        print('======== RegisterForm.full_clean =========*****************')
        # Cleaning data is done by:
        # 1) _clean_fields(): for each self.fields, calls field.clean() which will populate cleaned_data, in 3 stages:
        #     a) to_python() to coerce datatype or raise ValidationError if impossible
        #     b) validate() field-specific validation that is not suitable for a validator
        #     c) run_validators() runs all validators and aggregates into single ValidationError
        # 2) clean_<fieldname>() Takes no params, must return the cleaned value even if unchanged
        # 3) Form.clean() where we can deal with cross-field validations.
        super().full_clean()

    def create_form_user(self, **kwargs):
        """New user accounts can be created when submitting this form. """
        user = User.objects.create_user(
            **kwargs
            )
        return user

    def clean(self):
        print('======== RegisterForm.clean =========********************')
        cleaned_data = super().clean()
        input_email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        new_user = cleaned_data.get('new_user') == 'T'
        print(f'new user: {new_user}')
        billing_info = {
            'billing_address_1': cleaned_data['billing_address_1'],
            'billing_address_2': cleaned_data['billing_address_2'],
            'billing_city': cleaned_data['billing_city'],
            'billing_country_area': cleaned_data['billing_country_area'],
            'billing_postcode': cleaned_data['billing_postcode'],
            }
        if 'billing_country_code' in cleaned_data:
            billing_info['billing_country_code'] = cleaned_data['billing_country_code']
        data_new_user = {'first_name': first_name, 'last_name': last_name, 'email': input_email}
        data_new_user.update(billing_info)
        # there is no user inside the cleaned_data under any conditions
        user = self.initial['user']  # TODO: Test when user login changes after form load
        if new_user and hasattr(self, 'name_for_user') and hasattr(self, 'USERNAME_FLAG_FIELD'):  # OptionalUserName
            username_expected = cleaned_data.get(self.USERNAME_FLAG_FIELD, False)
            username = cleaned_data.get(self.name_for_user)
            if username_expected and username:
                data_new_user.update(username=username, username_not_email=True,)
                user = self.create_form_user(**data_new_user)
        if user.is_anonymous and new_user:  # They say they are new, but check to avoid collisions
            # Look by email
            same_email = User.objects.filter(email__iexact=input_email)
            if same_email.count():  # TODO: Change to .exists()
                found = same_email.filter(first_name__iexact=first_name, last_name__iexact=last_name).count()  # TODO: Change to .exists()
                if found:
                    message = "We found a user account with your name and email. "
                    message += "Try the login link, or resubmit the form and select you are a returning student. "
                    raise forms.ValidationError(_(message))
                    # If user was found, then we should have them login
                    # TODO: send user to login credentials, keep track of data they have given
                # TODO: Create a system to deal with matches
                # TODO: Either pass above queries to that function, or use .count() above.
            # Look by name
            same_name = User.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name)
            if same_name.count():  # TODO: Change to .exists()
                print('We found user(s) with that same name')
                message = "Are you sure you have not had classes with us? "
                message += "We have someone with that name already in our records. "
                message += "If this is you, either login or select you are a returning student. "
                message += "If this is not you, please resubmit with either a variation of your name or include an "
                # TODO: Create a system to deal with matching names, but are unique people
                message += "extra symbol (such as '.' or '+') at the end of your name to confirm your input"
                raise forms.ValidationError(_(message))
            # We can create this user
            user = self.create_form_user(**data_new_user)
        elif user.is_anonymous:  # new_user is False; User says they have an account, we should use that account.
            print('User says they are returning. They should login!')
            query_user = User.objects.filter(
                email__iexact=input_email,
                first_name__iexact=first_name,
                last_name__iexact=last_name,
                )
            user_count = query_user.count()
            if user_count > 1:
                print('MULTIPLE users with that email & name. We are using the first one.')
            # TODO: Create Logic when more than one user has the same email, for now using first match.
            user = query_user.first() if user_count > 0 else None  # TODO: refactor to use get_one_or_none ?
            # TODO: Anyone is allowed to add a user to classoffers (but no address update). Should login be required?
            if not user:
                message = "We did not find your user account with your name and email address. "
                message += "Try the login link. "
                message += "If that does not work, select that you are a new student and we can fix it later. "
                raise forms.ValidationError(_(message))
            # user = User.objects.find_or_create_for_anon(email=input_email, first_name=first_name, last_name=last_name)
            # TODO: What if a non-user is paying for a friend (established or new user)
        else:  # Existing users can update their billing address if they are logged in.
            for key, value in billing_info.items():
                if value:
                    setattr(user, key, value)
            user.save()
        print(f'user before paid_by_other check {user}')
        if cleaned_data.get('paid_by_other'):
            # We need to now get the billing info for user who is paying
            # Assign the logged in user name & email to paid_by
            paid_by = Student.objects.filter(user=user).first()  # TODO: ? instead use user.student
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
                    possible_users=possible_friends,
                    )
                # if that user needed to be created, a decorator will create the profile
            else:
                print('friend found without using find_or_create_by_name')
            user = friend
        print(f'user as used for student profile {user}')
        cleaned_data['student'] = Student.objects.get(user=user)  # TODO: ? instead use user.student
        print(f"student profile: {cleaned_data['student']}")
        print(f"class selected: {cleaned_data['class_selected']}")
        return cleaned_data

    def save(self, commit=True):
        print('======== Inside RegisterForm.save ===========')
        class_selected = self.cleaned_data.get('class_selected')
        student = self.cleaned_data.get('student')  # Profile for the User taking the ClassOffer
        paid_by = self.cleaned_data.get('paid_by')  # Profile for the User paying for the ClassOffer
        # TODO: Send confirmation email here? Or maybe do so with a decorator after save?
        email = Notify.register(selected=class_selected, student=student, paid_by=paid_by)
        if email:
            print(f"Email was sent for register of {student} paid by {paid_by}")
        else:
            print(f"Email ERROR for registering {student}")
        billing_info = {
            'billing_address_1': self.cleaned_data['billing_address_1'],
            'billing_address_2': self.cleaned_data['billing_address_2'],
            'billing_city': self.cleaned_data['billing_city'],
            'billing_country_area': self.cleaned_data['billing_country_area'],
            'billing_postcode': self.cleaned_data['billing_postcode'],
            }
        if 'billing_country_code' in self.cleaned_data:
            billing_info['billing_country_code'] = self.cleaned_data['billing_country_code']
        # Create payment for all, then a Registration for each class they selected.
        payment = Payment.objects.classRegister(
            register=class_selected,
            student=student,
            paid_by=paid_by,
            **billing_info
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


class PaymentForm(FocusMixIn, forms.ModelForm):
    """This is where a user inputs their payment data and it is processed. """

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
