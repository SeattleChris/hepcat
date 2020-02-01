# Feature Development Plan

## Milestones

| Complete           | Task                                      |
| ------------------ |:-----------------------------------------:|
|                    | **Start of Project**                      |
| :heavy_check_mark: | Research Django and needed packages. Overview site structure and features |
| :heavy_check_mark: | Setup: Docker, postgresql, Django, core packages, DB migrations, proof-of-life site |
|                    | **Milestone 1 Completion**                |
| :heavy_check_mark: | Models: User model module - student, teacher, admin.                |
| :heavy_check_mark: | Models: Subject, ClassOffer, Session - core product structure and inter-connections |
| :heavy_check_mark: | Models: Resource - allows both temporary or repeated resources |
| :heavy_check_mark: | Models: Profile & connected Resources - students get resources from their classoffers |
| :heavy_check_mark: | Admin Views: interface for Subject structure and planning specific ClassOffers.
| :heavy_check_mark: | Admin Views: interface for Session - planning future products, assigning publish times.
| :heavy_check_mark: | Admin Views: teacher/admin interface assigning resources (populates to students Profile)|
| :heavy_check_mark: | User Views: ClassOffer list (only currently open to join are shown), Register (join class)
| :heavy_check_mark: | User Views: Profile for user - see resources granted them, and class history.
|                    | **Milestone 2 Completion**           |
| :heavy_check_mark: | Models: Location - connect locations to ClassOffer |
| :heavy_check_mark: | User Views: AboutUs, ClassOffer details, Locations (directions) - core structure stubbed out |
| :heavy_check_mark: | Admin Views: Admin can assign class credit to any student (tracked in student Profile) |
| :heavy_check_mark: | Existing user joining a ClassOffer: Prompted to login. Catches if they already have account |
| :heavy_check_mark: | User onboarding: Can join ClassOffer, account created afterwards. No friction onboarding    |
| :heavy_check_mark: | User onboarding: Existing user can sign-up and/or pay for other users (existing or not)     |
| :heavy_check_mark: | Admin Views: Checkin - Each page for a day/location. Sections/class. Sorted by student name |
| :heavy_check_mark: | Metrics: Categorize students on their class progression - completed Beg and/or L2? (Profile)|
| :heavy_check_mark: | Design: Home page / landing site design. General pages layout design                        |
|                    | **Milestone 3 Completion**           |
|                    | Payment Processing: PayPal integration       |
|                    | Email Features: send register confirmations, weekly class emails         |
|                    | User Views: more filled out - student Profile structure, visual & layout of ClassOffers     |
|                    | User Views: About Us - show profile info for only teachers and staff, plus general business |
|                    | User Views: Contact Us (including contact form), Info - general site resources, sub-pages   |
|                    | User Views: General site clean up before first launch                                       |
|                    | Deploy Version 1.0: List classes, register, payment, manage resources, user onboarding      |
|                    | **Launch Version 1.0**           |
|                    | **Upcoming Features**           |
|                    | Interest tracking: update Profile model, forms for students, prompts sent to users.  |
|                    | Social Media connections on website: FB business page, FB group page, Twitter, etc.        |
|                    | Payment Processing: Square integration - on-site (in person) payments       |
|                    | Payment Processing: Stripe integration       |
|                    | User onboarding: integrate user accounts with Facebook/Google/etc login                     |
|                    | Email Features: Manage general customer emailing list        |
|                    | Metrics: Update class progression - include repeated L2, and higher levels                  |
|                    | Metrics: Typical follow-through rates in expected progression (at each step) |
|                    | Email Features: Better targeted messaging (depending on student's classoffer history)       |
|                    | Metrics: Identify groups outside of expected class progression |
|                    | Metrics: Identify customers "dropping off" to focus to re-gain them |
|                    | Email Features: Better targeted messaging (depending on other metrics analysis)             |
|                    | Email Features: improved weekly class emails, new resources available on profile, etc.      |
|                    | Email Features: Manage "contact us" messaging history        |
|                    | Metrics: Identify influencer customers - who improves likelihood of others also joining     |
|                    | Metrics Exploration: Are there other statistical groupings? |

## Checklist

### Key

- [x] Completed.
- [N] No: does not work or decided against.
- [ ] Still needs to be done.
- [?] Unsure if needed.
- [s] Stretch Goal. Not for current feature plan.

Current Status:
2020-01-30 14:17:45
<!-- Ctrl-Shift-I to generate timestamp -->

### Payment Processing

- [x] Can send needed data to PayPal payment site for user to complete payment process
- [x] Can receive authorization from PayPal (success url)
- [ ] Can check what email they used on PayPal for confirmation
  - [n] NO - ?Should a mis-match mean we change their email on file?
  - [ ] ?Should a mis-match change the 'paid by' field?
  - [ ] ?Should a single User account be allowed secondary associated email addresses?
- [ ] Fix: when getting authorization response, it falsely triggers user is not the same as paid_by
- [ ] Can take authorization, then capture amount through PayPal
- [ ] Can update student and checkin records with the completed payment amount
- [ ] If payment amount refunded or revoked, our records are also updated
- [ ] Checkin sheet is automatically updated with all online payment processes
- [ ] Manual process for managing on-site payments (with Square, Check, Cash)
- [ ] Login to newly created User account after they pay for their first ClassOffer
- [s] Automatically manage on-site credit card (via Square?) processing
- [s] Stripe payment integration
- [x] Update Subject (or ClassOffer) models to have price fields
- [x] Update price fields to auto-populate based on class type
- [ ] Update multi-class discount based on Subject/ClassOffer settings
- [ ] Instead of field saying 'billing_country_area' it should say 'State'
  - [ ] Simple fix: Change property to state, but modify when authorizing payments
  - [ ] Find some override: Displays as state, but tracks as field name.
  - [ ] Fix in fields list (add 'state'), then clean_state turns into field name
  - [ ] JS changes display based on country code or other field inputs
  - [ ] Create a Mixin: somehow fixes it whenever it comes up

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

## General Site

- [ ] Layout student Profile Resources & class history
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
