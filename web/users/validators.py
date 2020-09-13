import re
import unicodedata
from confusable_homoglyphs import confusables
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


CONFUSABLE = _("This name is not allowed. Please choose a different name. ")
CONFUSABLE_EMAIL = _("This email address is not allowed. Please supply a different email address. ")
DUPLICATE_EMAIL = _("This email address is already in use. Please supply a different email address. ")
DUPLICATE_USERNAME = _("A user with that username already exists. ")
FREE_EMAIL = _("Using free email addresses is not allowed. Please supply a different email address. ")
RESERVED_NAME = _("This name is reserved and cannot be used. ")
TOS_REQUIRED = _("You must agree to the terms to register. ")

HTML5_EMAIL_RE = (  # WHATWG HTML5 spec, section 4.10.5.1.5.
    r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]"
    r"+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
    r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)
# While not exhaustive, we can construct a list of names that probably should not be used.
# Some systems may use the username to create email addresses, or subdomains, or otherwise
# used as part of the URL path.
# Credit for basic idea and most of the list to Geoffrey Thomas's blog
# post about names to reserve:
# https://ldpreload.com/blog/names-to-reserve
SPECIAL_HOSTNAMES = [  # Hostnames with special/reserved meaning.
    "autoconfig",  # Thunderbird autoconfig
    "autodiscover",  # MS Outlook/Exchange autoconfig
    "broadcasthost",  # Network broadcast hostname
    "isatap",  # IPv6 tunnel autodiscovery
    "localdomain",  # Loopback
    "localhost",  # Loopback
    "wpad",  # Proxy autodiscovery
]
PROTOCOL_HOSTNAMES = [  # Common protocol hostnames.
    "ftp",
    "imap",
    "mail",
    "news",
    "pop",
    "pop3",
    "smtp",
    "usenet",
    "uucp",
    "webmail",
    "www",
]
CA_ADDRESSES = [  # Email addresses known used by certificate authorities during verification.
    "admin",
    "administrator",
    "hostmaster",
    "info",
    "is",
    "it",
    "mis",
    "postmaster",
    "root",
    "ssladmin",
    "ssladministrator",
    "sslwebmaster",
    "sysadmin",
    "webmaster",
]
RFC_2142 = [  # RFC-2142-defined names not already covered.
    "abuse",
    "marketing",
    "noc",
    "sales",
    "security",
    "support",
]
NOREPLY_ADDRESSES = [  # Common no-reply email addresses.
    "mailer-daemon",
    "nobody",
    "noreply",
    "no-reply",
]
SENSITIVE_FILENAMES = [  # Sensitive filenames.
    "clientaccesspolicy.xml",  # Silverlight cross-domain policy file.
    "crossdomain.xml",  # Flash cross-domain policy file.
    "favicon.ico",
    "humans.txt",
    "index.html"  # Added by Chris L Chapman
    "index.htm"  # Added by Chris L Chapman
    "keybase.txt",  # Keybase ownership-verification URL.
    "robots.txt",
    ".htaccess",
    ".htpasswd",
]
OTHER_SENSITIVE_NAMES = [  # Other names which could be problems depending on URL/subdomain structure.
    "aboutus",  # Added by Chris L Chapman
    "about-us",  # Added by Chris L Chapman
    "about_us",  # Added by Chris L Chapman
    "account",
    "accounts",
    "auth",
    "authorize",
    "blog",
    "buy",
    "cart",
    "clients",
    "contact",
    "contactus",
    "contact-us",
    "contact_us",  # Added by Chris L Chapman
    "copyright",
    "dashboard",
    "doc",
    "docs",
    "download",
    "downloads",
    "enquiry",
    "faq",
    "help",
    "inquiry",
    "license",
    "login",
    "logout",
    "me",
    "myaccount",
    "oauth",
    "pay",
    "payment",
    "payments",
    "plans",
    "portfolio",
    "preferences",
    "pricing",
    "privacy",
    "profile",
    "register",
    "secure",
    "settings",
    "signin",
    "signup",
    "ssl",
    "status",
    "store",
    "subscribe",
    "terms",
    "tos",
    "user",
    "users",
    "weblog",
    "work",
]
DEFAULT_RESERVED_NAMES = (
    SPECIAL_HOSTNAMES
    + PROTOCOL_HOSTNAMES
    + CA_ADDRESSES
    + RFC_2142
    + NOREPLY_ADDRESSES
    + SENSITIVE_FILENAMES
    + OTHER_SENSITIVE_NAMES
)


@deconstructible
class ReservedNameValidator:
    """ Disallow reserved names from form field values. """

    def __init__(self, reserved_names=DEFAULT_RESERVED_NAMES):
        self.reserved_names = reserved_names

    def __call__(self, value):
        if not isinstance(value, str):
            return
        if value in self.reserved_names or value.startswith(".well-known"):
            raise ValidationError(RESERVED_NAME, code="invalid")

    def __eq__(self, other):
        return self.reserved_names == other.reserved_names


@deconstructible
class CaseInsensitiveUnique:
    """ Check the value is unique, including ensuring it is case-insensitive unique. """

    def __init__(self, model, field_name, error_message):
        self.model = model
        self.field_name = field_name
        self.error_message = error_message

    def __call__(self, value):
        if not isinstance(value, str):
            return
        value = unicodedata.normalize("NFKC", value)
        if hasattr(value, "casefold"):
            value = value.casefold()  # pragma: no cover
        if self.model._default_manager.filter(
            **{"{}__iexact".format(self.field_name): value}
        ).exists():
            raise ValidationError(self.error_message, code="unique")

    def __eq__(self, other):
        return (
            self.model == other.model
            and self.field_name == other.field_name
            and self.error_message == other.error_message
        )


@deconstructible
class HTML5EmailValidator(RegexValidator):
    """ Use the HTML5 email address rules. """
    message = EmailValidator.message
    regex = re.compile(HTML5_EMAIL_RE)


def validate_confusables(value):
    """ Avoid mixed-script containing one or more characters in Unicode Visually Confusable Characters file. """
    if not isinstance(value, str):
        return
    if confusables.is_dangerous(value):
        raise ValidationError(CONFUSABLE, code="invalid")


def validate_confusables_email(value):
    """ For emails, avoid mixed-script characters in the Unicode Visually Confusable Characters file. """
    # The HTML5 specification states the RFC 5322 (governing email addresses) "defines
    # a syntax for e-mail addresses that is simultaneously too strict ... too vague
    # ...  and too lax ...  to be of practical use". Meanwhile, the HTML5 email validation
    # rule is self-admittedly (in section # 4.10.5.1.5) is a "willful violation" of
    # RFC 5322, to the submitted email address.
    #
    # We want to separately consider the local and domain parts of the email address.
    # We are simplifying this task by assuming that there must be exactly one '@' (U+0040),
    # and this separates the local and domain parts of the email address.
    if value.count("@") != 1:
        return
    local_part, domain = value.split("@")
    if confusables.is_dangerous(local_part) or confusables.is_dangerous(domain):
        raise ValidationError(CONFUSABLE_EMAIL, code="invalid")