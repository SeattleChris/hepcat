# hepcat

**Author**: Chris L Chapman
**Version**: 0.1.0 (increment the patch/fix version number up if you make more commits past your first submission)

## Overview

SeattleSwing - HepCat Productions offers services and classes in Swing Dance - Lindy Hop. This website will be used to manage new and existing customers signing up for a variety of classes offered. It will manage the current and upcoming class schedule details, as well has keep a record of previous class offering, attendence, and related information. It will manage the students as users of the website, and allow the class instructors and site admin to deliver weekly email and content to students in a given class as well as general users (all current and past students).

## Getting Started

clone the repo
make sure the file settings are correct.
docker-compose up --build

## Architecture

python 3.6-slim
Django 2.1.3
psycopg2-binary 2.7.6.1
django-registration 3.0
django-sass-processor 0.7.2
libsass 0.16.1
django-compressor 2.2
nginx
postgres

<!-- Provide a detailed description of the application design. What technologies (languages, libraries, etc) you're using, and any other relevant design information. This is also an area which you can include any visuals; flow charts, example usage gifs, screen captures, etc.-->

## API

The following routes have been made or scaffolled:

/                       home_view [defined in hepcat]
/admin/                 admin.site.urls
/user/register/         django_registration one_step.urls
/user/                  django.contrib.auth.urls
/classes/subject/       subject_list    SubjectListView     classwork/subject_list.html
/classes/subject/new/   subject_create  SubjectCreateView   classwork/subject_create.html
/classes/session/       session_list    SessionListView     classwork/session_list.html
/classes/session/new/   session_create  SessionCreateView   classwork/session_create.html
<!-- /classes/               published       PublishedListView   classwork/published.html -->


<!-- Provide detailed instructions for your applications usage. This should include any methods or endpoints available to the user/client/developer. Each section should be formatted to provide clear syntax for usage, example calls including input data requirements and options, and example responses or return values. -->

## Change Log

<!-- Ctrl+Shift+I (on Win & Linux) Inserts current DateTime, -->
2018-11-25 20:16:59  Docker rocket live. Just the hepcat project setup with nginx, static, db, web
2018-11-27 00:05:15  Scaffold routes. Session & Subject have models, list, create. Superuser added

