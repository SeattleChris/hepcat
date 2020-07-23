# hepcat

**Author**: Chris L Chapman
**Ver
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
  * A 'key day' should be determined as the one day that is most authoritative to determine dates.
    * This affects the default value for following class session, as well as other computed dates.
    * If there is a day that more reliably has classes for every session, this should be the key day.
    * If there are many reliable days, then slight advantage to set key day to the last week day.
* An admin can create new subjects (categories of offered classes), and various subject versions.
  * class levels are managed through subjects, as well as topics that don't fit as a class level.
  * A class level (subject) can have multiple versions.
        * Versions can be taken in any order, but all are expected before moving on to the next level.
* All approved classes will automatically be published on the appropriate day, determined by session.
* [Future] All proposed offered classes must approved before they are published to the public.
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
Sessions are periods of time that classes are offered. The offered class publish dates, the release of promotional material, publishing the weekly new resources for students of a given class, and many features are keyed off of the start of the class session (and also modified by other settings for offered classes). A key date is chosen for a session, but different classes during that session can start before or after it, which can be limited in range by a setting for the given session. Sessions are also set to last for a certain duration (usually the same duration of the offered classes), have a publish date, and an expiration date (for when to no longer publish these classes). The start and end dates are computed based on the settings for a session.

Subjects:
This is where most of the information is for an offered class is held, except for the details of what session (when it is offered), or any details that only apply to a specific instance/time that a class was offered. This includes the number of weeks it lasts, how long each class day is (in minutes), title, description, short description, promotional image, what class level (or if it is a non-level class) it is, etc. Class levels and versions are handled by Subject. At each level, there can be multiple versions. A student can expect that all these versions are at about the same level, so it does not matter which one they initially take or what order they take them in, but they should take all versions (except classes marked as NA version) before moving on to the next level. Higher level subjects (classes) will assume a student is familiar with the material of all of these lower level subject versions.

ClassOffer:
This is a specific subject, offered during a specific session. It includes information pertaining to this specific instance of it being offered, which includes the location, the teacher, the specific day and time, etc. A specific ClassOffer may have something occur that makes it slightly different from the other times this Subject is offered, so it may have additional or different resources or a modified syllabus & teacher's notes/class-plan associated with it.

## Getting Started

* Make sure you have a processing account through stripe and/or PayPal.
* Clone the repository.
* Create the needed database, recording the connection details to be used in `.env` file.
* Make sure the file settings are correct.
* Make an `.env` file, following the example of `.env_template`
* Create a virtual environment and install packages.
  * Using Pipenv:
    * `pipenv shell`
    * `pipenv install`
  * Using other virtual environments, as their typical usage.
* Move to `/web` directory for any of the following commands or locations for files and directories.
* Give execute privileges to the manage.py file. Make sure it executes using Python 3.
* Run `./manage.py migrate`
* Run `./manage.py createsuperuser`
  * input an admin username (this is temporary as it will be overwritten).
  * input an email and password as prompted (the email will be used as the username).
* Run `./manage.py runserver`
  * From here you should be able to login, but the username will be the provided admin email.
  * Go to the admin pages. Update the admin account with a first and last name.
  * Input the initial class structure content for: Session, Subject, ClassOffer
* Confirm `tests` directory is in the expected location.
* Create database test fixture from the basic starter models put into the live database.
  * `./manage.py dumpdata --indent 4 --exclude admin --exclude contenttypes > tests/db_basic.json`
  * Confirm the contents, possibly editing as needed, of `tests/db_basic.json`
  * Confirm all appropriate test classes load fixtures: `fixtures = ['tests/db_basic.json']`
  * Create other fixtures as needed and add them to the fixtures array in the appropriate tests class
* Move to top repo directory (if in '/web', then `cd ..`). Confirm tests work:
  * `./web/manage.py test`
* See [Tests] section below for further testing details and development.
* See [Deployment] section below for deploying on Python Anywhere, AWS, etc.
* ... More to be added later ...

<!-- **Alternative Setup Using Docker** -->

Each organization installing this app while have some unique settings. Some of these depend on the deployment and development environments, and some of these depend on the business/organization structure. While some of these organization structure settings are created as an organization admin after the app is installed, some are handled elsewhere, most notably in the `.env` file (which should never be published or shared publicly). The following has some `.env` file settings explained:

* SECRET_KEY: a unique, unpublished, key used by Django
* DEBUG: True during development. False for production deployment
* ALLOWED_HOSTS: space separated list - usually for development: 127.0.0.1 localhost 0.0.0.0
* DB_NAME: connection to the database (ie: postgres)
* DB_USER, DB_PASS, DB_HOST, DB_PORT: for connecting to the database
* EMAIL_HOST_USER, EMAIL_HOST_PASSWORD: allowing the app to send email
* STRIPE_PUBLIC_KEY, STRIPE_KEY: Public & Private keys, only needed if using stripe processing
* PAYPAL_EMAIL: If implementing PayPal payments, the email payments send their funds
* PAYPAL_SECRET: As given from PayPal developer dashboard credentials
* PAYPAL_CLIENT_ID: As given from PayPal developer dashboard credentials
* PAYPAL_URL: something like:
  * https://api.sandbox.paypal.com for development or
  * https://api.paypal.com for production
* BUSINESS_NAME: Optional - Can be used for templates in Admin site as well as main site.
* SUPERUSER_FIRST_NAME: used for creating superuser as first account
* SUPERUSER_LAST_NAME: used for creating superuser as first account
* DEFAULT_CITY: City most classes and/or most students are likely in.
* DEFAULT_COUNTRY_AREA_STATE: In the USA, this is the two-letter abbreviation for the State.
* DEFAULT_POSTCODE: In the USA, the zip code. Can be the short or long version (15 char max).
* DEFAULT_COUNTRY: Should be set to where you do the most business. No parameter if you don't want a default.
* ASSUME_CLASS_APPROVE: True or False for the default setting for 'manager approved' for ClassOffer and content.
* DEFAULT_CLASS_PRICE: Can set the common base price for most products (ClassOffer).
* DEFAULT_PRE_DISCOUNT: Can set the typical discount for paying in advanced (per product).
* MULTI_DISCOUNT: If offering a discount for multiple classes, this is the default value.
* DEFAULT_KEY_DAY: Integer for day of the week, counting up with Monday as 0.
* DEFAULT_MAX_DAY_SHIFT: A positive or negative number of days away from the key_day_date.
* DEFAULT_SESSION_WEEKS: The typical duration of class weeks for most Sessions.
* SESSION_MINIMUM_WEEKS: If a Session.num_weeks is less than this, it won't be considered in computed dates.
* DEFAULT_SESSION_EXPIRE: For a typical session, expire publishing it how many days after the first class?
* SHORT_SESSION_EXPIRE: For a session under minimum_weeks, expire publishing it how many days after the first class?
* DEFAULT_CLASS_MINUTES: The typical length of time of a single class day.

*Note: The last 18 are all optional pre-populated values, overwritable per product. For DEFAULT_CLASS_PRICE, DEFAULT_PRE_DISCOUNT, MULTI_DISCOUNT - whole numbers should have '.0' at the end.
The last seven are expected to be integers.

## Deployment

It should be possible to install this app on a variety of potential deployment locations, such as Google Cloud Platform, Amazon Web Service (AWS), Python Anywhere, Heroku, Digital Ocean, and others.

### Amazon Web Service - AWS

This app has been successfully installed on [Amazon Web Service (AWS)](https://aws.amazon.com/), using Elastic Beanstalk (EBS). The repo has an appropriate `.ebignore` file. Environment configuration templates can be found in the `.elasticbeanstalk/` to make `config.yml` and `01_env.config` files, respectively in each folder. These new files should never be added to the repo. The `.ebextensions` directory also has AWS EBS setup and management procedures used on AWS. In the hepcat app there is a management command added for creating the initial superuser (which is called by procedures in `.ebextensions`). The `.env` file should also be updated with appropriate AWS settings, such as setting `S3=True` to use S3 buckets, as well as various location definitions.

While AWS is an industry standard, it may not be the best choice for organizations that expect low or even medium usage.

### Python Anywhere

There are a low-cost and free tier options on [PythonAnywhere](https://www.pythonanywhere.com/). This may be appropriate for low, and possibly medium, volume users and organizations. The following detailed list is probably best if followed in the order listed.

* Create a user account on [PythonAnywhere](https://www.pythonanywhere.com/)
  * You can start with a free tier account and upgrade later if desired.
* Open a console from PythonAnywhere Dashboard:
  * Login to [Python Anywhere](https://www.pythonanywhere.com/)
  * New: Under Consoles, under 'New console:' click 'More...'. Then click 'Bash'.
  * Or use existing bash console if you have created one on here before.
  * You will be able to use the command line interface (CLI) in your browser.
* In console, git commands are available: clone the repo & move into the top repo directory.
* Use virtualenv from the root directory of the repo:
  * Open a console, move to the root directory of the repo (probably 'hepcat')
  * create for the first time: `mkvirtualenv myvirtualenv --python=/usr/bin/python3.7`
  * confirm python is in myvirtualenv: `which python`
  * stop env: `deactivate`
  * restart env: `workon myvirtualenv`
  * install packages: `pip install -r requirements.txt`
* Upload env file (can not be stored in repo):
  * On your local computer, update the '.env' file with the appropriate settings such as:
    * LIVE_ALLOWED_HOSTS, LIVE_WSGI_FILE, other LIVE_* variables, DB_* variables, etc.
  * In the PythonAnywhere Dashboard, click the 'Files' tab.
  * Under 'Directories' go to the repo root directory (probably ~/hepcat).
  * Under 'Files', click 'Upload a file', then select the '.env' file.
* Have the virtual environment use the '.env' file settings.
  * Open a console, and start the virtual env.
  * The following command should be modified with the appropriate user and virtualenv.
  * `echo 'set -a; source /home/<user>/hepcat/.env; set +a' >> /home/<user>/.virtualenvs/myvirtualenv/bin/postactivate`
  * Confirm env settings are used:
    * stop and restart env.
    * Type `printenv` and confirm some env values as expected from the file.
* Create Superuser for the app, as the initial admin.
  * On a console, with the virtual env running, navigate to the directory that has the 'manage.py' file.
  * Using the values in the '.env', via our custom command file: `./manage.py createsu`
  * Manually input email and password, using the default command: `./manage.py createsuperuser`
* Setup Web App on Python Anywhere
  * Login [Python Anywhere](https://www.pythonanywhere.com/) and click 'Web' tab on the Dashboard.
  * Choose 'Manual Configuration' for the desired python version (eg Python 3.7)
  * If needed, click 'Reload ...' button, and 'Run until 3 months from today'.
  * Update settings in 'Code:' Section.
    * Source code: `/home/<user>/hepcat/web` where 'manage.py' is located.
    * Working Directory: `/home/<user>`
  * Click WSGI file to edit: '[path-to-file]/[username]_pythonanywhere_com_wsgi.py'
    * Use the code below (after the bullet list) to:
      * Add path to 'manage.py' directory, reference settings file, and add dotenv functionality.
      * After saving the file, click the 'Reload ...' button at the top.
  * Update Virtualenv path under 'Virtualenv:' Section (adjust as needed):
    * `/home/<user>/.virtualenvs/<project_env_name>`
    * Click the 'Reload ...' button at the top to use this setting.
  * Update Static files section - for `/static/` and `/media/` files:
    * These should be in the same directory as the 'manage.py' file, eg
      * `/home/SeattleChris/hepcat/web/static`
      * `/home/SeattleChris/hepcat/web/media`
  * Optional: Enable 'Force HTTPS', then Reload (if wanted, perhaps change later).
  * Database Setup
    * on Python Anywhere Dashboard, click the 'Databases' tab
    * Make or confirm the database for the app, ideally something different than `<user>$default`.
    * Make sure the Database host, username, and password are set correctly in env and settings.
    * Start a console on the app database (click on it under 'Your databases)
      * Confirm the database is present, username is correct, etc. We don't expect tables yet.
    * Open a bash console, start virtualenv, and navigate to the directory with the 'manage.py' file.
    * Confirm the file has execute privileges (it probably does).
    * Migrate database with: `./manage.py migrate`
  * Prepare Static files and Media files:
    * Open a bash console, start virtualenv, and navigate to the directory with the 'manage.py' file.
    * Collect static files: `./manage.py collectstatic`
    * Collect media files: ???
  * View the site!
    * On Python Anywhere Dashboard, click the 'Web' tag.
    * Under 'Reload', click the 'Reload ...' button.
    * Go to the site url:
      * Link at the top of the Web tab of the Dashboard.
      * <username>.pythonanywhere.com
      * or custom domain.

Include the following code in [path-to-file]/[username]_pythonanywhere_com_wsgi.py

```Python
# +++++++++++ DJANGO +++++++++++
# To use your own Django app use code like this:
import os
import sys
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

project_folder = os.path.expanduser('~/hepcat')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# add your project directory to the sys.path
project_home = '/home/SeattleChris/hepcat/web'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# set environment variable to tell django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'hepcat.settings'

# serve django via WSGI
application = get_wsgi_application()
```

## Architecture

* python 3.7+
* boto3 1.14+
* Django 3.0+
  * django-registration 3.1+
  * django-payments 0.13.0
  * django-storages 1.9+
  * django-compressor 2.4
  * django-ses 1.0+
* psycopg2-binary 2.8+
* nginx
* postgres or MySQL
* Pillow 7+
* PayPal integration (django-payments 0.13+)
* stripe 2.48+
* coverage and django.test for tests.

Dev:

* django-sass-processor 0.7.5
* libsass 0.19.4
* coverage and django.test for tests.

## Development Progress

| Complete           | Core feature progress for Version 1.0 release |
| ------------------ |:-----------------------------------------:|
| :heavy_check_mark: | Models, Views, etc for planning and publishing class products (ClassOffer, Subject, Session)
| :heavy_check_mark: | User & Profile, w/ role permissions (customer, teacher, admin), login, no-friction onboarding
| :heavy_check_mark: | Resources assigned by staff to ClassOffer, or individually, incl. deliver to student/customer
| :heavy_check_mark: | About Us, Location, and general site content
| :heavy_check_mark: | Visual Design: Home page, general site design templates, assets, etc
| :heavy_check_mark: | Flow for student register & check-in - connect student to resources, admin check-in reports.
|                    | Payment Processing (PayPal first): generate & receive payment, track completed payments
|                    | Email management: confirm register, payment, weekly class announcement

We are keeping a checklist of upcoming tasks and feature development, as well as a more detailed summary of progress of the above core features. This is a live document, mostly describing the next steps in development. Currently focusing on PayPal integration, with summary and scratch pad notes linked below.

[Development Checklist](./checklist.md)

[Developer Notes - PayPal integration](./paypal.md)

## Tests

* Run test coverage setup:
  * If using Pipenv for virtual environment.
    * `coverage run --omit='*/virtualenvs/*' web/manage.py test -v 2`
  * Or if your virtual environment setup a `venv` directory:
    * `coverage run --omit='*/venv/*' web/manage.py test -v 2`
* View coverage report:
  * `coverage report`
  * `coverage html`
* Then view in browser at 'htmlcov/index.html'.
  * `browse htmlcov/index.html`
  * `chrome htmlcov/index.html`

## API

The following routes have been made or scaffolded (mostly in classwork app):

| **Route**          | **Path Name**     | **View**          | **Template**  |
| -------------------| ----------------- | ----------------- | ------------- |
| /classes/          | [classoffer_list] | ClassOfferListView| /classwork/classoffer_list |
| /location/<int:id> | [location_detail] | LocationDetailView| /classwork/location_detail.html |
| /location/         | [location_list]   | LocationListView  | /classwork/location_list.html |
| /checkin/          | [checkin]         | Checkin           | /classwork/checkin.html       |
| /register/         | [register]        | RegisterView      | /classwork/register.html      |
| /profile/          | [profile_page]    | ProfileView       | /classwork/user.html       |
| /resource/<int:id> | [resource_detail] | ResourceDetailView| /classwork/resource.html   |
| /                  | [home]    | home_view (hepcat.views)  | /home.view (uses base.html)|
| /payment/              | [payment]         | PaymentProcessView| /payment/payment.html  |
| /payment/fail/<int:id> | [payment_fail]    | PaymentProcessView| /payment/fail.html     |
| /payment/done/<int:id> | [payment_success] | PaymentProcessView| /payment/success.html  |
| /payments/             | -                        | (payments.urls)  | -                |
|  " process/<token>/    | [process_data]           | (payments.urls)  | -                |
|  " process/<variant>/  | [static_process_payment] | (payments.urls)  | -                |
| /admin/                | -                        |(admin.site.urls) | -                |
| **From our users app:**   |
| /user/signup/                 | ['signup']           | SignUp | signup.html             |
| /user/login/                  | ['login']                   |-| /django_registration/ ? |
| /user/logout/                 | [logout']                   |-| /django_registration/ ? |
| /user/password_change/        | ['password_change']         |-| /django_registration/ ? |
| /user/password_change/done/   | ['password_change_done']    |-| /django_registration/ ? |
| /user/password_reset/         | ['password_reset']          |-| /django_registration/ ? |
| /user/password_reset/done/    | ['password_reset_done']     |-| /django_registration/ ? |
| /user/reset/<uidb64>/<token>/ | ['password_reset_confirm']  |-| /django_registration/?  |
| /user/reset/done/             | ['password_reset_complete'] |-| /django_registration/ ? |

<!-- TODO: Update the payment url and view -->
<!-- /user/register/         django_registration one_step.urls -->
<!-- /user/                  django.contrib.auth.urls -->
