# Feature Development Plan

## Milestones

| Complete           | Task                                      |
| ------------------ |:-----------------------------------------:|
|                    | **Start of Project**                      |
| :heavy_check_mark: | Research Django and needed packages. Overview site structure and features             |
| :heavy_check_mark: | Setup: Docker, postgresql, Django, core packages, DB migrations, proof-of-life site   |
|                    | **Milestone 1 Completion**                |
| :heavy_check_mark: | Models: User model module - student, teacher, admin.                                       |
| :heavy_check_mark: | Models: Subject, ClassOffer, Session - core product structure and inter-connections        |
| :heavy_check_mark: | Models: Resource - allows both temporary or repeated resources                             |
| :heavy_check_mark: | Models: Profile & connected Resources - students get resources from their classoffers      |
| :heavy_check_mark: | Admin Views: interface for Subject structure and planning specific ClassOffers.            |
| :heavy_check_mark: | Admin Views: interface for Session - planning future products, assigning publish times.    |
| :heavy_check_mark: | Admin Views: teacher/admin interface assigning resources (populates to students Profile)   |
| :heavy_check_mark: | User Views: ClassOffer list (only currently open to join are shown), Register (join class) |
| :heavy_check_mark: | User Views: Profile for user - see resources granted them, and class history.
|                    | **Milestone 2 Completion**           |
| :heavy_check_mark: | Models: Location - connect locations to ClassOffer                                         |
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
|                    | Deployment Setup: Get App & DB on AWS (probably using Elastic Beanstalk)                    |
|                    | Email Features: send register confirmations, weekly class emails                            |
|                    | Payment & Student Sign Up: PayPal live working, email confirmations, added to checkin       |
|                    | User Views: more filled out - student Profile structure, visual & layout of ClassOffers     |
|                    | User Views: About Us - show profile info for only teachers and staff, plus general business |
|                    | User Views: Contact Us (including contact form), Info - general site resources, sub-pages   |
|                    | User Views: General site clean up before first launch                                       |
|                    | Deploy Version 1.0: List classes, register, payment, manage resources, user onboarding      |
|                    | **Launch Version 1.0**                                                                      |
|                    | **Upcoming Features**                                                                       |
|                    | Interest tracking: update Profile model, forms for students, prompts sent to users.         |
|                    | Social Media connections on website: FB business page, FB group page, Twitter, etc.         |
|                    | Payment Processing: Square integration - on-site (in person) payments                       |
|                    | Payment Processing: Stripe integration                                                      |
|                    | User onboarding: integrate user accounts with Facebook/Google/etc login                     |
|                    | Email Features: Manage general customer emailing list                                       |
|                    | Metrics: Update class progression - include repeated L2, and higher levels                  |
|                    | Metrics: Typical follow-through rates in expected progression (at each step)                |
|                    | Email Features: Better targeted messaging (depending on student's classoffer history)       |
|                    | Metrics: Identify groups outside of expected class progression                              |
|                    | Metrics: Identify customers "dropping off" to focus to re-gain them                         |
|                    | Email Features: Better targeted messaging (depending on other metrics analysis)             |
|                    | Email Features: improved weekly class emails, new resources available on profile, etc.      |
|                    | Email Features: Manage "contact us" messaging history                                       |
|                    | Metrics: Identify influencer customers - who improves likelihood of others also joining     |
|                    | Metrics Exploration: Are there other statistical groupings?                                 |

## Checklist

### Key

- [x] Completed.
- [N] No: does not work or decided against.
- [ ] Still needs to be done.
- [c] Likely completed, but needs to be Confirmed.
- [?] Unsure if needed.
- [s] Stretch Goal. Not for current feature plan.

Current Status:
2020-02-27 15:13:10
<!-- Ctrl-Shift-I to generate timestamp -->

### Deployment on AWS

- [x] Setup Elastic Beanstalk with EC2 Instance
- [x] Refactor old docker-compose to plain Django app setup
- [x] Setup application to work with local DB
- [x] Deploy application without database setup (to EC2)
- [ ] Setup Elastic Beanstalk with a Database (DB) Instance
  - [x] Temp solution: DB instance deleted when environment terminated
  - [ ] Setup [Amazon RDS](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.RDS.html)
- [x] Setup Static files
  - [x] Temp solution: static files in the EC2 server
  - [x] Better solution: [use S3](https://realpython.com/deploying-a-django-app-to-aws-elastic-beanstalk/#static-files)
  - [x] It seems many online sources suggest using the following package
  - [x] [Use package for S3](https://django-storages.readthedocs.io/en/latest/index.html)
- [x] Setup a superuser account command on deploy.
- [ ] Get Media files working like static (02_django.config)
- [ ] Change PayPal and Stripe secrets
- [ ] Change EMAIL_HOST_PASSWORD, maybe EMAIL_HOST_USER
- [x] Change SECRET_KEY
- [c] Decide make migrations approach
  - [x] Always do the command locally, then when pushing to deployed it does the migrations
  - [n] Make it another command in the `03_db-and-static.config` file.
- [x] Get local dev setup to connect to live DB server.
- [ ] [gzip via Apache Config](https://realpython.com/deploying-a-django-app-to-aws-elastic-beanstalk/)
  - [ ] Seems to break?
- [ ] gzip Static (and Media) files? done by: AWS_IS_GZIPPED = True
- [ ] Security improvement - Fix DB security group settings far too open (allowing any local dev to connect)

### Payment Processing

- [x] Can send needed data to PayPal payment site for user to complete payment process
- [x] Can receive authorization from PayPal (success url)
- [ ] Can check what email they used on PayPal for confirmation
  - [n] NO - ?Should a mis-match mean we change their email on file?
  - [ ] ?Should a mis-match change the 'paid by' field?
  - [ ] ?Should a single User account be allowed secondary associated email addresses?
- [x] Fix: correctly identify if paid_by vs user signed up for class are different.
- [x] Can take authorization, then capture amount through PayPal
- [c] Can update student and checkin records with the completed payment amount
- [ ] If payment amount refunded or revoked, our records are also updated
- [c] Checkin sheet is automatically updated with all online payment processes
- [ ] Manual process for managing on-site payments (with Square, Check, Cash)
- [ ] Login to newly created User account after they pay for their first ClassOffer
- [s] Automatically manage on-site credit card (via Square?) processing
- [s] Stripe payment integration
- [x] Update Subject (or ClassOffer) models to have price fields
- [x] Update price fields to auto-populate based on class type
- [ ] Maybe combine Checkin view with ClassOfferListView - diff in sort and templates.
- [ ] Add items as Many-to-Many field to make Payments easier to use a orders.
- [c] Mark All associated Registration models when payment captured in full.
- [ ] Handle partial payment structure, especially if multi-class discount was given.
- [c] Update multi-class discount based on Subject/ClassOffer settings
- [x] Instead of field saying 'billing_country_area' it should say 'State'
  - [n] Simple fix: Change property to state, but modify when authorizing payments
  - [x] Use verbose_name: Displays as state, but tracks as field name.
  - [n] Fix in fields list (add 'state'), then clean_state turns into field name
  - [n] JS changes display based on country code or other field inputs
  - [x] Use help_text: Gives extra variations of state, territory, province and zip vs postal code.
  - [n] Create a Mixin: somehow fixes it whenever it comes up
- [ ] Update verbose_name and help_text in users/models.py

## Email Features

- [ ] Setup email handling for the site/app
- [ ] Send confirmation on register
- [ ] Send weekly class emails on a schedule (wait for confirmation/adjustment?)
- [ ] Allow Teacher or Admin to send an unexpected class email (what if Snow closure)
- [ ] Subscribe the current teacher and appropriate admin to current class email list
- [ ] Manage current class email subscriptions
- [ ] Send emails submitted to Contact Us page
- [s] Manage "Contact Us" messaging history
- [s] Manage general student email subscriptions

## Style & Layout

- [ ] Layout student Profile Resources & class history
- [ ] Improve Class Sign Up - Registration form.
- [ ] Update instructions and method for "If you want to register a different person then ..."
  - [x] Registration Form should have initial values for user that is logged in.
  - [ ] Registration Form should have initial value for state based on the User model default.
  - [ ] CSS Style of save/submit button
  - [ ] Alignment of input fields
    - [ ] Field boxes all line up, field names on left with align right
    - [ ] ? Address formatted like normal address lines?
    - [ ] Move returning student question lower in form
    - [ ] Field 'help_text' adjusted in CSS
      - [ ] less prominent text (smaller? lighter font?)
      - [ ] placed under the input box?

## General Site

- [ ] 'About Us' page should only show staff members.
- [ ] Deal with when admin has no name (such as a superuser), it may break the 'About Us' page.
- [ ] Login Page should say email instead of username
- [ ] Hi message should use name instead of username (email)
- [ ] On Profile, add link to update profile/user details (billing, email, etc)
- [ ] Add content and connect to "Info" link button.
- [ ] Profile model: update highest_level to not include "current" classoffer.
- [ ] Auto-Login new user if created on their first ClassOffer sign up.
- [ ] User: create update view and method
- [ ] Profile details view: add note for completed Beg and/or L2
- [ ] About Us page shows only teacher & staff profile info, plus business info. Links to Contact Us.
- [ ] Contact Us page w/ contact form (send to email)
- [ ] Add interesting dance images to ClassOffer list view, maybe detail view also
- [ ] Decide if we host a weekly current class page (as old site), or refactor to student's Profile view?
- [ ] Create space for "Info" page: general site resources and sub-pages
  - [ ] Music
  - [ ] Go out dancing
  - [s] At your Party?
  - [s] Private lessons?
  - [s] ??
- [ ] Review all completed site pages for consistency, including different view sizes.
- [ ] Deploy development site
- [ ] Deploy production site
