# Feature Development Plan

## Milestones

| Complete           | Task                                                                                        |
| ------------------ |:-------------------------------------------------------------------------------------------:|
|                    | **Start of Project**                                                                        |
| :heavy_check_mark: | Research Django and needed packages. Overview site structure and features                   |
| :heavy_check_mark: | Setup: Docker, postgresql, Django, core packages, DB migrations, proof-of-life site         |
|                    | **Milestone 1 Completion**                                                                  |
| :heavy_check_mark: | Models: User model module - student, teacher, admin.                                        |
| :heavy_check_mark: | Models: Subject, ClassOffer, Session - core product structure and inter-connections         |
| :heavy_check_mark: | Models: Resource - allows both temporary or repeated resources                              |
| :heavy_check_mark: | Models: Profile & connected Resources - students get resources from their classoffers       |
| :heavy_check_mark: | Admin Views: interface for Subject structure and planning specific ClassOffers.             |
| :heavy_check_mark: | Admin Views: interface for Session - planning future products, assigning publish times.     |
| :heavy_check_mark: | Admin Views: teacher/admin interface assigning resources (populates to students Profile)    |
| :heavy_check_mark: | User Views: ClassOffer list (only currently open to join are shown), Register (join class)  |
| :heavy_check_mark: | User Views: Profile for user - see resources granted them, and class history.               |
|                    | **Milestone 2 Completion**                                                                  |
| :heavy_check_mark: | Models: Location - connect locations to ClassOffer                                          |
| :heavy_check_mark: | User Views: AboutUs, ClassOffer details, Locations (directions) - core structure stubbed out|
| :heavy_check_mark: | Admin Views: Admin can assign class credit to any student (tracked in student Profile)      |
| :heavy_check_mark: | Existing user joining a ClassOffer: Prompted to login. Catches if they already have account |
| :heavy_check_mark: | User onboarding: Can join ClassOffer, account created afterwards. No friction onboarding    |
| :heavy_check_mark: | User onboarding: Existing user can sign-up and/or pay for other users (existing or not)     |
| :heavy_check_mark: | Admin Views: Checkin - Each page for a day/location. Sections/class. Sorted by student name |
| :heavy_check_mark: | Metrics: Categorize students on their class progression - completed Beg and/or L2? (Profile)|
| :heavy_check_mark: | Design: Home page / landing site design. General pages layout design                        |
|                    | **Milestone 3 Completion**                                                                  |
| :heavy_check_mark: | Payment Processing: PayPal integration (sandbox)                                            |
| :heavy_check_mark: | Deployment Setup: Get App & DB on AWS (probably using Elastic Beanstalk)                    |
| :heavy_check_mark: | Deployment Setup: Get App & DB on PythonAnywhere (using MySQL)                              |
| :heavy_check_mark: | Admin: Sessions pre-populate and error correct dates of the session                         |
| :heavy_check_mark: | Tests: Add initial testing including coverage reports                                       |
| :heavy_check_mark: | Tests: Checking date computations on Session model and Admin form                           |
| :heavy_check_mark: | Tests: UserHC model - create user; Profile create on UserHC; Basics for all models.         |
| :heavy_check_mark: | User Views: Profile - resources filtered to currently allowed and no duplicates.            |
|                    | User Views: Profile - resources display, layout, and navigation in a useful way.            |
| :heavy_check_mark: | User Views: About Us - show profile info for only teachers and staff, plus general business |
|                    | User Views: Contact Us (including contact form), Info - general site resources, sub-pages   |
|                    | User Views: General site clean up before first launch                                       |
|                    | User Views: Social Justice Call                                                             |
|                    | **Soft Launch**                                                                             |
|                    | **Milestone 4 Completion**                                                                  |
| :heavy_check_mark: | Tests: Models for classwork, users, and associated data                                     |
|                    | Tests: Views for classwork                                                                  |
| :heavy_check_mark: | Tests: Admin functionality and views                                                        |
|                    | Tests: User resources and profile view                                                      |
|                    | User Views: more filled out - student Profile structure, visual & layout of ClassOffers     |
|                    | Payment & Student Sign Up: PayPal live working, email confirmations, added to checkin       |
|                    | Email Features: send register confirmations, weekly class emails                            |
|                    | Initial Social Media connections on website: FB business page, FB group page                |
|                    | Deploy Version 1.0: List classes, register, payment, manage resources, user onboarding      |
|                    | **Launch Version 1.0**                                                                      |
|                    | **Upcoming Features**                                                                       |
|                    | Email Features: Manage general customer emailing list                                       |
|                    | User onboarding: integrate user accounts with Facebook/Google/etc login                     |
|                    | Metrics: Update class progression - include repeated L2, and higher levels                  |
|                    | Metrics: Typical follow-through rates in expected progression (at each step)                |
|                    | Email Features: Better targeted messaging (depending on student's classoffer history)       |
|                    | Tests: Email features                                                                       |
|                    | Tests: Payment features                                                                     |
|                    | Social Media connections on website: FB business page, FB group page, Twitter, etc.         |
|                    | Metrics: Identify groups outside of expected class progression                              |
|                    | Metrics: Identify customers "dropping off" to focus to re-gain them                         |
|                    | Email Features: Better targeted messaging (depending on other metrics analysis)             |
|                    | Interest tracking: update Profile model, forms for students, prompts sent to users.         |
|                    | Payment Processing: Square integration - on-site (in person) payments                       |
|                    | Payment Processing: Stripe integration                                                      |
|                    | Email Features: improved weekly class emails, new resources available on profile, etc.      |
|                    | Email Features: Manage "contact us" messaging history                                       |
|                    | Metrics: Identify influencer customers - who improves likelihood of others also joining     |
|                    | Metrics Exploration: Are there other statistical groupings?                                 |
|                    | Tests: Metrics features                                                                     |
|                    | Tests: Coverage for most of the code                                                        |

## Checklist

### Key

- [x] Completed.
- [N] No: does not work or decided against.
- [ ] Still needs to be done.
- [c] Likely completed, but needs to be Confirmed.
- [?] Unsure if needed.
- [s] Stretch Goal. Not for current feature plan.

Current Status:
2020-08-25 18:11:14
<!-- Ctrl-Shift-I to generate timestamp -->

### Bug Fixes

- [x] Teacher reference in ClassOffer listing (update now that teachers are many-to-many with classoffers.)
- [x] ClassOffer Manager computing dates: Fix when the 'class_day' is just beyond the range of 'max_day_shift'.
- [x] ProfileView fix listing of each resource (currently shows dictionaries)
- [x] ClassOffer manager and model methods for returning Resources attached by ClassOffer or Subject.
  - [x] Initial tests.
  - [x] Tests fully covering new features.
- [n] ?Should tests use `django.utils.timezone`?
- [n] ?Should tests use [django.utils.dateparse](https://docs.djangoproject.com/en/3.0/ref/utils/)?
- [ ] Regain Admin feature: able to create/attach Resources.
- [x] Profile view: current solution does not have access to Resource.get_absolute_url() method for each one.
- [x] Update Tests to reflect changing Resource to ManyToMany with Subject and with ClassOffer
- [x] Datetime math issues
  - [x] Database current 'date' math should be in utc.
  - [x] Setting a Date (no time) for a Session should not get messed up by timezone issues.
    - [x] After midnight, now=date.today() or dt.combine(now, time(0)), with either CURDATE or UTC_DATE.
    - [x] Afternoon: CURDATE or UTC_DATE
    - [x] Evening: UTC_DATE misses when avail_week + expire == 3, but CURDATE does not!
- [ ] Profile not created if Admin page creates a new Staff User or Student User.

### Optimization and Structure improvements

- [x] Look into methods for Session model prev_session and next_session.
  - [x] instance methods .get_next_by_FOO and .get_previous_by_FOO for Session model next and previous
    - [x] Does not work on unsaved models, which may be our main use case for these properties.
  - [x] QuerySet methods latest(<field_name>) and earliest(<field_name>)
- [ ] Check for any model properties that should use `key_lazy` or `key_lazy_text` or `cached_property`?
  - [ ] [key_lazy utils](https://docs.djangoproject.com/en/3.0/ref/utils/#django.utils.functional.cached_property)
  - [ ] [cached_property](https://docs.djangoproject.com/en/3.0/ref/utils/#django.utils.functional.cached_property)
- [ ] Revisit `success_url` for RegisterView, PaymentProcessView
  - [ ] `success_url = reverse_lazy('author-list')` in the View class is an option, but ...
    - [ ] You don’t even need to provide a success_url for CreateView or UpdateView
      - [ ] they will use get_absolute_url() on the model object if available.
      - [ ] [Generic Views](https://docs.djangoproject.com/en/3.0/topics/class-based-views/generic-editing/)
- [ ] Look into Login restrictions
  - [ ] `@login_required` decorator.
  - [ ] `LoginRequiredMixin` for any view class that must have login?
- [x] Is the current User model using an EmailValidator, or should this be updated?
  - [x] [EmailValidator](https://docs.djangoproject.com/en/3.0/ref/validators/)
- [ ] ? Update [HTTP Error Handlers](https://docs.djangoproject.com/en/3.0/ref/urls/) ?
- [ ] Using [reverse_lazy](https://docs.djangoproject.com/en/3.0/ref/urlresolvers/) well?
- [ ] [select_related](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#django.db.models.query.QuerySet.select_related)
- [ ] Revisit [Optimization techniques](https://docs.djangoproject.com/en/3.0/topics/db/optimization/)
  - [ ] Profile the actual cost to ensure the refactor is actually cheaper for our context.
  - [ ] Create well designed database indexes
    - [ ] [meta](https://docs.djangoproject.com/en/3.0/ref/models/options/#django.db.models.Options.indexes)
    - [ ] [Field.db_index]
  - [ ] If only need id, use foreign key directly: e.g. `entry.blog_id` is cheaper than `entry.blog.id`
  - [ ] Use QuerySet `select_related()` and `prefetch_related()` and `prefetch_related_objects()`
  - [ ] Use `QuerySet.defer()` and `QuerySet.only()`
  - [ ] Use QuerySet `update()` and `delete()` instead of loading and saving individually.

### Tests

- [x] Tests: use [django.utils.module_loading](https://docs.djangoproject.com/en/3.0/ref/utils/)
  - [x] `tests/views/test_views.py` file
  - [x] other files
- [x] Unit tests setup using django test
- [x] Coverage tests setup with coverage
- [ ] Models full or near full coverage
  - [x] Initial tests of models
  - [x] Scaffold method names for what coverage report shows is missing
- [ ] Views full or near full coverage
  - [x] Scaffold method names for what coverage report shows is missing
  - [ ] Initial tests for views
- [x] Admin full or near full coverage
  - [x] Initial tests for admin
- [x] Session date computation methods
- [x] Admin forms for Session: date computations
- [ ] Payment features full or near full coverage
  - [ ] Initial tests for payment features
- [ ] Email features full or near full coverage
  - [ ] Initial tests for email features
- [ ] Resource and user profile view features full or near full coverage
  - [ ] Initial tests for user profile view and resource features
- [ ] Metrics features full or near full coverage
  - [ ] Initial tests for metrics features

### Metrics

- [ ] Update class progression - include repeated L2, and higher levels
- [ ] Typical follow-through rates in expected progression (at each step)
- [ ] Identify groups outside of expected class progression
- [ ] Identify customers "dropping off" to focus to re-gain them
- [ ] Identify influencer customers - who improves likelihood of others also joining
- [ ] Exploration: Are there other statistical groupings?

### Deployment on PythonAnywhere

- [?] Stop the AWS servers.
- [x] Update code to use MySQL since it is preferred on this platform.
- [x] Upload ver 0.4.0
- [x] Update models and migrations.
- [x] Get Database and code working.
- [x] Collect static working.
- [x] Upload ver 0.4.1.
- [x] Upload ver 0.4.4.
- [x] Update Docs for deployment instructions.
- [ ] Upload ver 0.4.6.
- [ ] Populate initial Class structure models.

### Deployment on AWS

- [x] Setup Elastic Beanstalk with EC2 Instance
- [x] Refactor old docker-compose to plain Django app setup
- [x] Setup application to work with local DB
- [x] Deploy application without database setup (to EC2)
- [x] Setup Elastic Beanstalk with a Database (DB) Instance
  - [x] Temp solution: DB instance deleted when environment terminated
  - [x] Setup [Amazon RDS](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.RDS.html)
  - [x] [Decouple DB](https://aws.amazon.com/premiumsupport/knowledge-center/decouple-rds-from-beanstalk/)
    - [x] Create an RDS DB snapshot
    - [x] Safeguard your Amazon RDS DB instance from deletion
    - [x] Create a new Elastic Beanstalk environment
      - [x] Create environment B.
      - [x] Connect environment B to the existing Amazon RDS instance of environment A.
      - [x] Verify that environment B can connect to the existing Amazon RDS instance and that your application functions as expected.
    - [x] Perform a blue/green deployment to avoid downtime
    - [x] Remove the security group rule for the old Elastic Beanstalk environment
    - [x] Delete the stack
    - [x] Confirm working
- [x] Setup Static files
  - [x] Temp solution: static files in the EC2 server
  - [x] Better solution: [use S3](https://realpython.com/deploying-a-django-app-to-aws-elastic-beanstalk/#static-files)
  - [x] It seems many online sources suggest using the following package
  - [x] [Use package for S3](https://django-storages.readthedocs.io/en/latest/index.html)
- [x] Setup a superuser account command on deploy.
- [ ] Get Media files working like static (02_django.config)
- [ ] Confirm it works with Debug is False.
- [ ] Change PayPal and Stripe secrets
- [ ] Change EMAIL_HOST_PASSWORD, maybe EMAIL_HOST_USER
- [x] Change SECRET_KEY
- [c] Decide make migrations approach
  - [x] Always do the command locally, then when pushing to deployed it does the migrations
  - [n] Make it another command in the `03_db-and-static.config` file.
- [x] Get local dev setup to connect to live DB server.
- [x] [gzip via Apache Config](https://realpython.com/deploying-a-django-app-to-aws-elastic-beanstalk/)
  - [?] Seems to break?
- [ ] gzip Static (and Media) files? done by: AWS_IS_GZIPPED = True
- [ ] Security improvement - Fix DB security group settings far too open (allowing any local dev to connect)
- [ ] Save DB and other settings in S3. Setup ebextensions rules to retrieve from S3.

### Payment Processing

- [x] Can send needed data to PayPal payment site for user to complete payment process
- [ ] Fix PayPal return url.
- [x] Can receive authorization from PayPal (success url)
- [x] Update register form to use blank defaults if we have an Anonymous user
- [x] Sign up form only shows current published classes.
- [ ] Can check what email they used on PayPal for confirmation
  - [n] NO - ?Should a mis-match mean we change their email on file?
  - [ ] ?Should a mis-match change the 'paid by' field?
  - [ ] ?Should a single User account be allowed secondary associated email addresses?
- [x] Fix: correctly identify if paid_by vs user signed up for class are different.
- [x] Can take authorization, then capture amount through PayPal
- [c] Can update student and checkin records with the completed payment amount
- [s] If payment amount refunded or revoked, our records are also updated
- [c] Checkin sheet is automatically updated with all online payment processes
- [s] Manual process for managing on-site payments (with Square, Check, Cash)
- [ ] Login to newly created User account after they pay for their first ClassOffer
- [s] Automatically manage on-site credit card (via Square?) processing
- [s] Stripe payment integration
- [x] Update Subject (or ClassOffer) models to have price fields
- [x] Update price fields to auto-populate based on class type
- [ ] Maybe combine Checkin view with ClassOfferListView - diff in sort and templates.
- [ ] Add items as Many-to-Many field to make Payments easier to use a orders.
- [c] Mark All associated Registration models when payment captured in full.
- [s] Handle partial payment structure, especially if multi-class discount was given.
- [c] Update multi-class discount based on Subject/ClassOffer settings
- [x] Instead of field saying 'billing_country_area' it should say 'State'
  - [n] Simple fix: Change property to state, but modify when authorizing payments
  - [x] Use verbose_name: Displays as state, but tracks as field name.
  - [n] Fix in fields list (add 'state'), then clean_state turns into field name
  - [n] JS changes display based on country code or other field inputs
  - [x] Use help_text: Gives extra variations of state, territory, province and zip vs postal code.
  - [n] Create a Mixin: somehow fixes it whenever it comes up
- [x] Update verbose_name and help_text in users/models.py
- [x] Update verbose_name and help_text for payments

### Email Features

- [ ] Setup email handling for the site/app
- [x] Setup 6swing1.com email
- [ ] Send confirmation on register
  - [x] Running Local (with DEBUG = False)
  - [x] Running on Server, to and from verified email addresses.
  - [ ] Live, from admin to external email address
- [ ] Send weekly class emails on a schedule (wait for confirmation/adjustment?)
- [ ] Allow Teacher or Admin to send an unexpected class email (what if Snow closure)
- [ ] Subscribe the current teacher and appropriate admin to current class email list
- [ ] Manage current class email subscriptions
- [ ] Send emails submitted to Contact Us page
- [s] Manage "Contact Us" messaging history
- [s] Manage general student email subscriptions

### Admin class scheduling

- [x] Session model has awareness of the next_session and prev_session
- [x] Session model has callable to compute some default date values
- [x] Session model has clean methods that can be optionally called to correct dates
- [x] Session model is aware of its potential start_date and end_date, which is not simply just the key_day_date
- [x] Session model end_date accounts for skipped weeks that only affect some class days and not others
- [x] Session save method can call optionally call full_clean, but will auto-correct some date fields
- [x] Admin form for Session will raise ValidationError if session dates overlap
- [x] Admin form, after ValidationError, will repopulate the fields with values suggested from Session model clean
- [x] Resources for Subjects, ClassOffers or Other auto-determine Resource.related_type
- [x] Raise ValidateError if Session classes overlap.
- [x] Raise ValidateError if other issues with Session.
- [x] Session.clean modifies values to ensure the new Session does not overlap with existing Sessions.
- [x] On Admin Session ValidateError, repopulate the fields with new values from Session.clean method.
- [x] ClassOffer will be assigned dates according to their Session.
- [x] ClassOffer will handle invalid day of the week inputs.
- [x] ClassOffer Admin list: show start and end dates.
- [x] ClassOffer Admin list: show start and end times in nice-display (not military time)

### General Admin Features

- [ ] Groups: Allow for some hierarchial and cross-group organizational structures (see Sign Up & User Accounts)
  - [ ] Hierarchial: If they are in a child group, they are automatically added to a parent group
  - [ ] Cross-Group: A group is a role modifier. So similarities of Teacher: Group-X vs Admin: Group-X.
- [ ] ? Optional fixtures for example class structure?

### Sign Up & User Account Creation Features

- [x] Django-registration: basic user creation method
- [x] Django-registration: can create a user without asking for a username input
- [ ] Django-registration: integration, managing our computed username.
- [ ] Django-registration: Catch username IntegrityError:
  - [ ] ? Confirm with user they are not the existing user?
  - [ ] Recompute username.
- [ ] ? Create a username validator that first tries the email, then concatenated name value.
- [x] Update login pages to say 'email' where it currently asks for 'username'.
- [ ] ? Class sign up integrated with django-registration?
- [ ] Class sign up as anonymous process:
  - [x] Create the account, sign-up for class, allow payment.
  - [ ] User is logged in on account creation?
  - [ ] Auto-Login new user if created on their first ClassOffer sign up.
  - [ ] Password for Users created by class sign-up:
    - [ ] ? User has a randomly generated password, prompted to change on next login.
    - [ ] ? User confirms with email link. Prompted for password from the link.
    - [ ] ? No mention of password until user attempts to login.
  - [ ] If user never confirms, it does not stop them from joining future class.
- [x] Admin for Users has proxy models to view Staff or Student users. Users can still be both.
  - [x] These proxy models are not linked to from external apps. They only affect views in Admin.
- [x] Separate Profile models for Students and Staff
  - [x] A user can have both, one of each.
  - [x] If a user has both, can navigate to either one.
  - [x] If a user has both, displays a default of staff profile.
- [ ] Listener to always create Profile on new User, as well as always update. Connected one-to-one, cascade deletes.
  - [x] Working when only one Profile model (not both Staff and Student profile models).
  - [x] Working with both Staff and Student profile models.
  - [ ] Working with Proxy User models for Staff and Student

### Form Views - Style & Layout

- [x] Auto-focus first (or critical) field.
- [ ] Name input: First and Last default to same line if screen size allows.
- [ ] Address input: City, State, Zip default to same line if screen size allows.
- [x] Address input: Address1 and Address2 on separate lines with explanation of continued input.
- [ ] Label and Input box line up across different rows
  - [ ] ? Using table layout?
  - [ ] ? Using non-table layout?
- [ ] CSS Style of save/submit button
- [ ] Field boxes all line up, field names on left with align right
- [ ] Field 'help_text' adjusted in CSS
  - [ ] less prominent text (smaller? lighter font?)
  - [ ] placed under the input box?
- [ ] Improve Class Sign Up - Registration form.
  - [ ] Update instructions and method for "If you want to register a different person then ..."
  - [ ] Move returning student question lower in form
  - [x] Registration Form should have initial values for user that is logged in.
  - [x] Registration Form should have initial value for state based on the User model default.

### Profile and Resource Views

- [x] Profile: Resources filtered to currently available.
- [x] Profile: Resources no duplicates.
- [x] Profile: Resources displayed and can be navigated in a useful way.
- [x] List of associated classes.
- [x] List of resources by type.
- [ ] ? Profile details view: add note for completed Beg and/or L2
- [ ] Resources can be listed by classoffer.
- [ ] Advertise next appropriate classoffer for this student.
- [ ] Resource section of Recent or New resources.
- [ ] Another page/view for older resources.
- [x] How to manage if they are both Staff and a Student?
  - [x] There is a unique link to their Staff profile view and their Student profile view.
  - [x] On their default profile view, there is a link to the other profile.
- [ ] Staff Profiles:
  - [x] Staff Profile: What info do they want as a staff view? Or just handle that in the admin views?
  - [x] have bio
  - [x] an ordering field for desired placement in "about us" view
  - [x] Can be removed from "about us" page by admin.
  - [x] Distinction between teacher and other admin
  - [x] More refined staff roles managed by groups, allowing them to be dynamic for future admin.
- [ ] Student Profiles:
  - [x] Student have fields and methods for connecting to ClassOffers, Resources, and inspecting customer data.
- [ ] See Admin Feature: Allow for some hierarchial and cross-group organizational structures.
  - [ ] Display of what groups they are a part of.
    - [ ] ? Only if more than teacher and admin (or student)?

### Other Views - Style & Layout

- [x] About Us - Shows only Teachers and Staff.
- [x] About US - order of teacher & staff info can be controlled by an admin.
- [x] Utilize get_absolute_url for all detail views.
- [ ] Check if display_session values need `escape_uri_path` because of possible spaces or other user input oddities.
  - [ ] [escape_uri_path](https://docs.djangoproject.com/en/3.0/ref/utils/#django.utils.functional.cached_property)
- [ ] Add content and connect to "Info" link button.
- [ ] Decide if we host a weekly current class page (as old site), or refactor to student's Profile view?
- [ ] Create space for "Info" page: general site resources and sub-pages
  - [ ] Music
  - [ ] Go out dancing
  - [s] At your Party?
  - [s] Private lessons?
  - [s] ??
- [ ] General Site Contact Us View/Page
  - [ ] On-site contact form (send to email)
- [ ] About Us Links to Contact Us.
  - [ ] Individual contacts for each staff member?

### General Site

- [x] 'About Us' page should only show staff members.
- [x] More consistent Model str and repr methods.
- [x] Fix max_length to 191 for utf8mb4.
- [x] About Us page shows only teacher & staff profile info, plus business info.
- [x] Deal with when admin has no name (such as a superuser), it may break the 'About Us' page.
- [x] Login Page should say email instead of username
- [x] Hi message should use name instead of username (email)
- [x] On Profile, add link to update profile/user details (billing, email, etc)
- [ ] Profile model: update highest_level to not include "current" classoffer.
- [x] User: create update view and method
- [ ] Add interesting dance images to ClassOffer list view, maybe detail view also
- [ ] Review all completed site pages for consistency, including different view sizes.
- [ ] Deploy development site
- [ ] Deploy production site
