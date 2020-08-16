# Development Notes

For development and deployments notes.

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
* Run `./manage.py createsu` which creates a superuser based on '.env' file settings.
  * Alternative: `./manage.py createsuperuser`
    * input an admin username (this is temporary as it will be overwritten).
    * input an email and password as prompted (the email will be used as the username).
    * This approach may have difficulties with the lack of a name, which may need to be fixed directly in the database.
* Run `./manage.py runserver`
  * From here you should be able to login, but the username will be the provided admin email.
  * Go to the admin pages. Confirm the admin account has a first and last name, or update as needed.
  * Confirm the admin has both a Staff and a Student user profile (in the CLASSWORK section).
  * Create data for testing - Input the initial class structure content in the recommended order:
    * Session: Give a key_day_date old enough to be expired now. Manually set the publish date in the past.
    * Subject: Attach a Resource when making this model.
    * ClassOffer: Should use the Session and Subject just made. You can create a Location here as well.
  * Input initial 'Site Content' with a title of 'business_about' to be included in the about us page.
  * Create a test or mock Payment and Registration
    * If payments are on test mode, then use the site's process, paying mind to the PAYPAL_BUYER or other test buyer.
      * Running locally, you'll get a 'This site can’t be reached' error, but will populate the database as needed.
    * If payments are live, a mock version should be created for use in a test database for tests later on.
  * Input other initial content for each model, aka row in the admin section of CLASSWORK.
* Confirm `tests` directory is in the expected location.
* Create database test fixture from the basic starter models put into the live database.
  * `./manage.py dumpdata --indent 4 --exclude admin --exclude contenttypes > ../tests/fixtures/db_basic.json`
    * Or modify the end of that line to reflect the desired location for your test data fixtures.
  * Confirm the contents, possibly editing as needed, of `tests/db_basic.json`.
    * Move any model data from  'users.userhc' or 'classwork.payment' to a new file named `db_hidden.json` in fixtures.
    * Move any other model data with sensitive information (should not be public), to the `db_hidden.json` file.
  * Confirm all appropriate test classes load fixtures: `fixtures = ['tests/db_basic.json', 'db_hidden.json', ]`.
  * Create other fixtures as needed and add them to the fixtures array in the appropriate tests class.
* Move to top repo directory (if in '/web', then `cd ..`).
  * Confirm the `.gitignore` file excludes the `.env` and `*hidden.json` files, and others as needed.
  * Confirm tests work with the command: `./web/manage.py test`
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
* SESSION_LOW_WEEKS: If a Session.num_weeks is less than this, it won't be considered in computed dates.
* SESSION_MAX_WEEKS: The longest any session can last. Used for potential resources before Session.num_weeks is known.
* DEFAULT_SESSION_EXPIRE: For a typical session, expire publishing it how many days after the first class?
* SHORT_SESSION_EXPIRE: For a session under minimum_weeks, expire publishing it how many days after the first class?
* DEFAULT_CLASS_MINUTES: The typical length of time of a single class day.
* COMMON_LEVELS_COUNT: The number of levels that are almost always run (each level can have multiple versions).

*Note: The last 20 are all optional pre-populated values, overwritable per product. For DEFAULT_CLASS_PRICE, DEFAULT_PRE_DISCOUNT, MULTI_DISCOUNT - whole numbers should have '.0' at the end.
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
        * Notice that created databases actual name will be prepended with `<username>$`.
        * Choose a good password, and make sure you know the full name and password to put into the '.env' file.
    * On the PythonAnywhere Dashboard, click the 'Consoles' tab:
      * Make sure the `.env` file has the correct settings for the database, stop and start the virtual environment.
      * On bash console (w/ virtual env) navigate to the `hepcat/web` directory (or where `manage.py` is located).
      * Confirm the 'manage.py' file has execute privileges (it probably does).
      * Use the migrate manager command `./manage.py migrate` to create the database tables.
  * Create Superuser for the app, as the initial admin.
    * On a console, with the virtual env running, navigate to the directory that has the 'manage.py' file.
    * Using the values in the '.env', via our custom command file: `./manage.py createsu`
      * Or manually input email and password, using the default command: `./manage.py createsuperuser`
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
  * If using Pipenv for virtual environment: either of following, second one omits coverage report of tests themselves.
    * `coverage run --omit='*/virtualenvs/*' web/manage.py test -v 2`
    * `coverage run --omit='*/virtualenvs/*','*/tests/*' web/manage.py test -v 2`
  * Or if your virtual environment setup a `venv` directory: the following are with or without coverage report of tests.
    * `coverage run --omit='*/venv/*' web/manage.py test -v 2`
    * `coverage run --omit='*/venv/*','*/tests/*' web/manage.py test -v 2`
  * Additional files and directories can be ignored as additional comma separated list for omit value
* View coverage report:
  * `coverage report`
  * `coverage html`
* Then view in browser at 'htmlcov/index.html', depending on your settings:
  * `browser htmlcov/index.html`
  * `browse htmlcov/index.html`
  * `chrome htmlcov/index.html`
