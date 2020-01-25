# hepcat

**Author**: Chris L Chapman
**Version**: 0.2.0

## Overview

Primarily this is designed for the needs of HepCat Productions - www.SeattleSwing.com, with the intent it could be useful for other dance schools or educational organizations that offer weekly classes. This website will be used to manage new and existing customers signing up for a variety of classes offered. It will manage the current and upcoming class schedule details, keep a record of previously offered classes, attendance, and related information. It will manage the students as users of the website, and allow the class instructors and site admin to deliver weekly email and content to students in a given class as well as general users (all current and past students).

## Features

* The site can accept payment via Stripe and PayPal (possibly other payment methods, TBD).
* Payments are tracked with the class sign up. Reconciling should usually take no additional steps.
* The upcoming classes are published automatically, through the use of Session, and approval by admin.
* Resources are scheduled to be published to students in an offered class by the teachers and the admin
  * This can include things such as review videos, announcements, links to information, etc.
* Students can view the history of classes they have attended.
* Students can access the videos & other resources that were made available any time in the past.
  * Some resources can be set to expire if they are something like a short-lived announcement.
* Teachers have access to class planning notes and other resources targeted to help their instruction.
* Teachers have access to their student list and get information about their student experience level.
* Admins have a quick view to check student payments and track attendance.
* Admins can modify the public site, resources, user roles, etc. to meet the needs of the school.

### Student User Features

* A student, with a user account, has access to resources as scheduled by admins & teachers.
* A user account is *not* required for new students to sign up and pay for a class series.
  * A user account is automatically made, and this student will have an opportunity to activate it.
  * If a student activates their account, they gain access for resources for all attended classes.
* A new, or existing, student can be signed up, and paid for, by an existing or anonymous user.
  * All user account opportunities are available to a student attending the class
    * Just the same if they had signed up themselves.
  * Just because someone signed up & paid, does not mean they get access to the user account info.
* Referrals (if program activated) are tracked when new students identify who referred them.
* Students, with active user accounts, receive weekly class emails and resources.
  * Of course, students can opt-in/out of any email postings. They can access via their account.
  * This feature can be turned off or modified by the admin.
* A student can send a review of a class, of a teacher, and of an admin or organization in general.
  * The student can choose to keep their feedback anonymous (by default) or not.

### Teacher Features

* A teacher can send a message to all the students in a class they are currently teaching.
  * This generally is a weekly email (for opt-in students) or via students account.
  * Content can be scheduled in advance, including defaults for the class in general.
    * This can include prepared videos, "Welcome to class" or "Thanks for finishing" messages.
* A teacher will be given a list of students in their class with a synopsis of their experience.
  * A teacher can look more specifically at the class history of one of their current students.
* A teacher has access to default resources for their offered class (and associated subject).
* A teacher can add additional resources for their current class or to the overall subject.
* For potential future class offerings, a teacher can submit a title, description, resources, etc.
  * This will need to be approved by an admin before it is published as offered by the school.
  * This teacher maintains edit rights so they can use the site for their class ideas.
* A teacher has access to the syllabus for any class they teach, and all class levels below it.
* A teacher has access to the class plan for any class/subject they teach.
  * The teacher can maintain notes on the site for a current class plan modifications and progress.
  * Both the initial class plan, and the notes held during the run of class, are saved.
    * This can be helpful for investigating if the intended plan should be modified.
* A teacher has a profile which can include a photo and a teacher bio to be published on the site.
* A teacher can review the results of student feedback (students kept anonymous).

### Admin Features

* An admin has all of the features that a teacher has and can view the features available to students.
* An admin can deactivate the weekly class emails, or referral feature, as appropriate for the school.
* An admin can create new sessions (periods of time a class is offered) and assign start dates.
  * Many automatic publish times for classes offered, resources, emails, etc are determined by this.
* An admin can create new subjects (categories of offered classes), and various subject versions.
  * class levels are managed through subjects, as well as topics that don't fit as a class level.
  * A class level (subject) can have multiple versions.
        * Versions can be taken in any order, but all are expected before moving on to the next level.
* All proposed offered classes must be flagged as accepted before they are published to the public.
* An admin has a report for offered classes listing student names and payment status.
  * Most of the payment reconciliation should be automatically handled by the site.
  * Admins are given access to reconcile any unclear payments.
  * if needed, an admin can contact a student to request a payment or clarify any uncertainties.
* An admin can keep a record of attendance.
  * This can be helpful for viewing if a student missed a session or if a class had attendance issues.
* As needed, an admin can assign class credits & discounts to students to manage unusual circumstances.
* An admin can modify any of the content, resources, and details for the class scheduling features.
* An admin can create additional resources on the site for the public, or teachers, or students.
* An admin has access to all the student reviews submitted and the tools needed to respond accordingly.
* An admin can schedule promotional material for upcoming offered classes (and assign who receives it)
* An admin can define patterns of attendance to view and make business decisions for student groups.
  * This can help discover the effectiveness of the school's class structure.
  * This can identify and help reach out to students that may need personal attention.
  * This can be used to filter promotional material instead of blasting everyone with the same message.
* An admin can create additional user roles as needed, and assign different privileges accordingly.
  * This could be useful if there was a teaching assistant role or other staff with different needs.

## How Offered Classes are Organized

Sessions:
Sessions are periods of time that classes are offered. The offered class publish dates, the release of promotional material, publishing the weekly new resources for students of a given class, and many features are keyed off of the start of the class session (and also modified by other settings for offered classes). A key date is chosen for a session, but different classes during that session can start before or after it, which can be limited in range by a setting for the given session. Sessions are also set to last for a certain duration (usually the same duration of the offered classes), have a publish date, and an expiration date (for when to no longer publish these classes).

Subjects:
This is where most of the information is for an offered class is held, except for the details of what session (when it is offered), or any details that only apply to a specific instance/time that a class was offered. This includes the number of weeks it lasts, how long each class day is (in minutes), title, description, short description, promotional image, what class level (or if it is a non-level class) it is, etc. Class levels and versions are handled by Subject. At each level, there can be multiple versions. A student can expect that all these versions are at about the same level, so it does not matter which one they initially take or what order they take them in, but they should take all versions (except classes marked as NA version) before moving on to the next level. Higher level subjects (classes) will assume a student is familiar with the material of all of these lower level subject versions.

ClassOffer:
This is a specific subject, offered during a specific session. It includes information pertaining to this specific instance of it being offered, which includes the location, the teacher, the specific day and time, etc. A specific ClassOffer may have something occur that makes it slightly different from the other times this Subject is offered, so it may have additional or different resources or a modified syllabus & teacher's notes/class-plan associated with it.

## Getting Started

* Make sure you have a processing account through stripe and/or PayPal
* clone the repo
* make sure the file settings are correct.
* make an `.env` file, following the example of `.env_template`
* docker-compose up --build
* ... To Be Filled In Later ...

Each organization installing this app while have some unique settings. Some of these depend on the deployment and development environments, and some of these depend on the business/organization structure. While some of these organization structure settings are created as an organization admin after the app is installed, some are handled elsewhere, most notably in the `.env` file (which should never be published or shared publicly). The following has some `.env` file settings explained:

SECRET_KEY: a unique, unpublished, key used by Django
DEBUG: True during development. False for production deployment
ALLOWED_HOSTS: space separated list - usually for development: 127.0.0.1 localhost 0.0.0.0
DB_NAME: connection to the database (ie: postgres)
DB_USER, DB_PASS, DB_HOST, DB_PORT: for connecting to the database
EMAIL_HOST_USER, EMAIL_HOST_PASSWORD: allowing the app to send email
STRIPE_PUBLIC_KEY, STRIPE_KEY: Public and Private keys, only needed if implementing stripe payment processing
PAYPAL_EMAIL: If implementing PayPal payments, the email payments send their funds
PAYPAL_SECRET: As given from PayPal developer dashboard credentials
PAYPAL_CLIENT_ID: As given from PayPal developer dashboard credentials
PAYPAL_URL: something like https://api.sandbox.paypal.com for development or https://api.paypal.com for production
DEFAULT_CLASS_PRICE: Optional - Can set the common base price for most products (ClassOffer)
DEFAULT_PRE_DISCOUNT: Optional - Can set the typical discount for paying in advanced (per product)
MULTI_DISCOUNT: Optional - If offering a discount for multiple classes, this is the default value
*Note: The above 3 are the pre-populated values, overwritable per product. Whole numbers should have '.0' at the end.

## Architecture

* python 3.6-slim
* Django 3.0.2
* psycopg2-binary 2.8.4
* django-registration 3.0.1
* nginx
* postgres
* django-compressor 2.4
* django-payments 0.13.0
* Pillow 7.0.0
* PayPal integration (django-payments)
* Future Features: stripe 2.42.0

Dev:

* django-sass-processor 0.7.5
* libsass 0.19.4

## API

The following routes have been made or scaffolded (mostly in classwork app):

| **Route**          | **Path Name**     | **View**          | **Template**  |
| -------------------| ----------------- | ----------------- | ------------- |
| /classes/          | [classoffer_list] | ClassOfferListView| /classwork/classoffer_list |
| /location/<int:id> | [location_detail] | LocationDetailView| /classwork/location_detail.html |
| /location/         | [location_list]   | LocationListView  | /classwork/location_list.html |
| /checkin/          | [checkin]         | Checkin           | /classwork/checkin.html       |
| /register/         | [register]        | RegisterView      | /classwork/register.html      |
| /profile/             | [profile_page]    | ProfileView       | /classwork/user.html       |
| /resource/<int:id>    | [resource_detail] | ResourceDetailView| /classwork/resource.html   |
| /                     | [home]    | home_view (hepcat.views) | /home.view (uses base.html) |
| /payment/             | [payment]         | PaymentProcessView| /payment/payment.html      |
| /payment/fail/<int:id>| [payment_fail]    | PaymentResultView | /payment/fail.html         |
| /payment/done/<int:id>| [payment_success] | PaymentResultView | /payment/success.html      |
| /payments/               | -         |       ( payments.urls ) |
| /admin/               | -         |       ( admin.site.urls ) |
| **From our users app:**   |
| /user/signup/         | ['signup']        | SignUp            | signup.html |
| /user/login/                | [name='login']              |-| /django_registration/ ? |
| /user/logout/               | [name='logout']             |-| /django_registration/ ? |
| /user/password_change/      | [name='password_change']    |-| /django_registration/ ? |
| /user/password_change/done/|[name='password_change_done'] |-| /django_registration/ ? |
| /user/password_reset/     | [name='password_reset']       |-| /django_registration/ ? |
| /user/password_reset/done/ | [name='password_reset_done'] |-| /django_registration/ ? |
| /user/reset/<uidb64>/<token>/|[name='password_reset_confirm']|-|/django_registration/?|
| /user/reset/done/     | [name='password_reset_complete'] |-| /django_registration/ ? |

<!-- TODO: Update the payment url and view -->
<!-- /user/register/         django_registration one_step.urls -->
<!-- /user/                  django.contrib.auth.urls -->
