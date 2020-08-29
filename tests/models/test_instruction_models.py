from django.test import TestCase, TransactionTestCase
from django.conf import settings
from django.db.models import Max, Subquery
from unittest import skip
from .helper_models import SimpleModelTests, Resource, UserHC, Student, Session, Subject, ClassOffer
from datetime import date, time, timedelta, datetime as dt


class SubjectModelTests(SimpleModelTests, TestCase):
    Model = Subject
    # detail_url_name = 'subject_detail'  # Does Not Exist
    repr_dict = {'Subject': 'name', 'Level': 'level', 'Version': 'version'}
    str_list = ['_str_slug']
    defaults = {'name': 'test model'}


class ClassOfferModelTests(SimpleModelTests, TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_hidden.json']
    Model = ClassOffer
    detail_url_name = 'classoffer_detail'
    repr_dict = {'Class Id': 'id', 'Subject': 'subject', 'Session': 'session'}
    str_list = ['subject', 'session']
    defaults = {}

    def test_manager_queryset_resources_no_expire(self):
        sess = Session.objects.first()
        res_count = Resource.objects.count()
        initial_max_level = ClassOffer.objects.all().aggregate(Max('_num_level')).get('_num_level__max', 0)
        no_res_results = ClassOffer.objects.filter(_num_level__gt=initial_max_level).resources()
        avail, expected_resources = 0, []  # expire will always be 0
        for lvl, display in Subject.LEVEL_CHOICES[:2]:
            res_lvl = Resource.objects.create(
                content_type='text',
                name='_'.join((lvl, 'all', str(avail), '0')),
                user_type=1,
                avail=avail,
                expire=0)
            res_lvl.save()
            res_count += 1
            expected_resources.append(res_lvl)
            for ver, _ in Subject.VERSION_CHOICES[:3]:
                subj = Subject.objects.create(name='_'.join((lvl, ver)), level=lvl, version=ver)
                subj.save()
                res = Resource.objects.create(
                    content_type='text',
                    name='_'.join((lvl, ver, str(avail), '0')),
                    user_type=1,
                    avail=avail,
                    expire=0)
                res.save()
                res_count += 1
                expected_resources.append(res)
                subj.resources.add(res, res_lvl)
                co = ClassOffer.objects.create(subject=subj, session=sess, start_time=(time(17, 0)))
                co.save()
                avail = 0 if avail + 1 > sess.num_weeks else avail + 1
        expected_names = [getattr(ea, 'name', '') for ea in expected_resources]
        actual_resources = ClassOffer.objects.resources()
        actual_names = [ea.get('name', '') for ea in actual_resources]

        self.assertTrue(len(no_res_results) == 0)
        self.assertLessEqual(sess.end_date, date.today())
        self.assertLessEqual(sess.end_date, dt.utcnow().date())
        self.assertEqual(res_count, Resource.objects.count())
        self.assertSetEqual(set(expected_names), set(actual_names))

    def test_manager_queryset_resources_various_expire(self):
        """ Making many ClassOffers that today is the week 3 class with resources on all weeks with 0 <= expire < 3. """
        user = UserHC.objects.create_user(email="fake@faker.com", password='test12', first_name='fa', last_name='la')
        user.save()
        student = user.student
        now = date.today()
        cur_week = 3
        start = now - timedelta(days=7*(cur_week - 1))
        start_string = start.strftime('%Y-%m-%d')  # TODO: Remove after confirmation
        day = start.weekday()
        sess_cur = Session.objects.create(name="Sess Cur", key_day_date=start, publish_date=start - timedelta(days=14))
        sess_cur.save()
        if start_string != sess_cur.key_day_date.strftime('%Y-%m-%d'):  # TODO: Remove after confirmation
            raise ArithmeticError(f"Session key_day_date set to {start_string}, but value is {sess_cur.key_day_date} ")
        res_total_count = Resource.objects.count()
        res_expected = []
        avail, expire, res_goal_count = 0, 0, 0
        for lvl, display in Subject.LEVEL_CHOICES:
            student_has_level = False
            res_lvl = Resource.objects.create(
                content_type='text',
                name='_'.join((lvl, 'all', str(avail % 3), '0')),
                user_type=1,
                avail=(avail % 3),
                expire=0)
            res_lvl.save()
            res_total_count += 1
            for ver, _ in Subject.VERSION_CHOICES:
                subj = Subject.objects.create(name='_'.join((lvl, ver)), level=lvl, version=ver)
                subj.save()
                co = ClassOffer.objects.create(subject=subj, session=sess_cur, start_time=(time(17, 0)), class_day=day)
                co.save()
                student.taken.add(co)
                res = Resource.objects.create(
                    content_type='text',
                    name='_'.join((lvl, ver, str(avail), str(expire))),
                    user_type=1,
                    avail=avail,
                    expire=expire)
                res.save()
                res_total_count += 1
                subj.resources.add(res, res_lvl)
                avail_week = 1 if avail == 0 else avail
                if avail <= cur_week and (expire == 0 or (avail_week + expire) >= cur_week):
                    res_goal_count += 1 if student_has_level else 2
                    res_expected.append(res)
                    if not student_has_level:
                        res_expected.append(res_lvl)
                        student_has_level = True
                if avail + 1 > sess_cur.num_weeks:
                    avail = 0
                    expire = (expire + 1) % 3
                else:
                    avail += 1
        student.save()
        expected_names = [getattr(ea, 'name', '') for ea in res_expected]
        actual_names = [ea.get('name', '') for ea in student.taken.resources()]
        classoffers_created_count = len(Subject.LEVEL_CHOICES) * len(Subject.VERSION_CHOICES)  # 80

        self.assertEqual(classoffers_created_count, student.taken.count())
        self.assertEqual(res_total_count, Resource.objects.count())
        self.assertNotEqual(res_total_count, res_goal_count)
        self.assertSetEqual(set(actual_names), set(expected_names))
        self.assertEqual(res_goal_count, len(student.taken.resources()))

    def test_manager_queryset_resources_with_user_kwarg(self):
        student = Student.objects.first()
        sess = Session.objects.first()
        initial_max_level = ClassOffer.objects.all().aggregate(Max('_num_level')).get('_num_level__max', 0)
        no_res_results = ClassOffer.objects.filter(_num_level__gt=initial_max_level).resources()
        classoffers = student.taken.all()
        expected_res = []
        for ea in list(classoffers) + [ea.subject for ea in classoffers]:
            expected_res.extend([res for res in ea.resources.all() if res not in expected_res])
        for res in expected_res:
            res.expire = 0
            res.save()
        res_count = Resource.objects.count()
        classoffer_count = student.taken.count()  # TODO: ClassOffer.objects.count() is more accurate?
        avail, expire = 0, 0
        subset_subj_level = 2 if len(Subject.LEVEL_CHOICES) > 3 else 0
        subset_subj_version = 3 if len(Subject.VERSION_CHOICES) > 3 else 0
        for lvl, display in Subject.LEVEL_CHOICES[subset_subj_level:]:
            student_has_level = False
            res_lvl = Resource.objects.create(
                content_type='text',
                name='_'.join((lvl, 'all', str(avail), str(expire))),
                user_type=1,
                avail=avail,
                expire=expire)
            res_lvl.save()
            res_count += 1
            for ver, _ in Subject.VERSION_CHOICES[subset_subj_version:]:
                subj = Subject.objects.create(name='_'.join((lvl, ver)), level=lvl, version=ver)
                subj.save()
                res = Resource.objects.create(
                    content_type='text',
                    name='_'.join((lvl, ver, str(avail), str(expire))),
                    user_type=1,
                    avail=avail,
                    expire=expire)
                res.save()
                res_count += 1
                subj.resources.add(res, res_lvl)
                co = ClassOffer.objects.create(subject=subj, session=sess, start_time=(time(17, 0)))
                co.save()
                classoffer_count += 1
                if classoffer_count % 2:
                    student.taken.add(co)
                    expected_res.append(res)
                    if not student_has_level:
                        expected_res.append(res_lvl)
                        student_has_level = True
                avail = 0 if avail + 1 > sess.num_weeks else avail + 1
        actual_res = student.taken.resources(user=student.user)
        actual_res_names = set([ea.get('name', '') for ea in actual_res])
        expected_res_names = set([getattr(ea, 'name', '') for ea in expected_res])

        self.assertTrue(len(no_res_results) == 0)
        self.assertLessEqual(sess.end_date, date.today())
        self.assertLessEqual(sess.end_date, dt.utcnow().date())
        self.assertEqual(res_count, Resource.objects.count())
        self.assertEqual(classoffer_count, ClassOffer.objects.count())
        self.assertSetEqual(expected_res_names, actual_res_names)
        self.assertEqual(len(expected_res), len(actual_res))

    def test_manager_get_resources_as_subquery(self):
        classoffers = ClassOffer.objects.all()
        expected_res = []
        for ea in list(classoffers) + [ea.subject for ea in classoffers]:
            expected_res.extend([res for res in ea.resources.all() if res not in expected_res])
        for res in expected_res:
            res.expire = 0
            res.save()
        expected_names = [getattr(ea, 'name', '') for ea in expected_res]
        res = ClassOffer.objects.get_resources().order_by().values('name')[:1]
        result = ClassOffer.objects.annotate(recent_resource=Subquery(res))
        actual_names = [ea.recent_resource for ea in result]

        self.assertEqual(len(expected_res), len(result))
        self.assertSetEqual(set(expected_names), set(actual_names))

    def test_manager_resources_params_student_user(self):
        student = Student.objects.first()
        sess = Session.objects.first()
        new_co = ClassOffer.objects.create(subject=Subject.objects.first(), session=sess, start_time=time(19, 0))
        student.taken.add(new_co)
        taken = student.taken.all()
        res_by_classoffer = ClassOffer.objects.resources(user=student)
        res_by_taken = student.taken.resources()

        self.assertSetEqual(set([repr(ea) for ea in taken]), set([repr(ea) for ea in ClassOffer.objects.all()]))
        self.assertEqual(len(res_by_classoffer), len(res_by_taken))
        self.assertTrue(all(ea in res_by_taken for ea in res_by_classoffer))

    def test_manager_resources_params_start_and_end(self):
        with self.assertRaises(TypeError):
            ClassOffer.objects.get_resources(start='bad', end='bad', skips=0, type_user=0, max_weeks=0)
        # end test_manager_resources_params_start_and_end

    def test_manager_resources_params_skips(self):
        end = date.today()
        start = end - timedelta(days=14)
        with self.assertRaises(TypeError):
            ClassOffer.objects.get_resources(start=start, end=end, skips='bad', type_user=0, max_weeks=0)

    def test_manager_resources_params_type_user_str(self):
        end = date.today()
        start = end - timedelta(days=14)
        with self.assertRaises(TypeError):
            ClassOffer.objects.get_resources(start=start, end=end, skips=0, type_user='bad', max_weeks=0)

    def test_manager_resources_params_type_user_int(self):
        end = date.today()
        start = end - timedelta(days=14)
        with self.assertRaises(TypeError):
            ClassOffer.objects.get_resources(start=start, end=end, skips=0, type_user=('bad', 'input', ), max_weeks=0)

    def test_manager_resources_params_live_by_date(self):
        start = date.today() - timedelta(days=21)
        sess = Session.objects.create(name="test manager", key_day_date=start, publish_date=start)
        subj = Subject.objects.create(version=Subject.VERSION_CHOICES[0][0], name='clean subj')
        new_res_expired = Resource.objects.create(content_type='text', user_type=0, avail=1, expire=1, name="Missed")
        new_res_live = Resource.objects.create(content_type='text', user_type=0, avail=1, expire=0, name="Live")
        new_co = ClassOffer.objects.create(subject=subj, session=sess, start_time=time(19, 0))
        new_res_expired.save()
        new_res_live.save()
        new_co.save()
        subj.resources.add(new_res_expired, new_res_live)
        expected_res = [new_res_live]
        res_by_classoffer = ClassOffer.objects.get_resources(model=new_co, live=False, live_by_date=True)
        all_res_by_classoffer = ClassOffer.objects.get_resources(model=new_co, live=False)
        expected_all_res = expected_res + [new_res_expired]

        self.assertEqual(len(res_by_classoffer), len(expected_res))
        self.assertSetEqual(set([repr(ea) for ea in expected_res]), set([repr(ea) for ea in res_by_classoffer]))
        self.assertEqual(len(all_res_by_classoffer), len(expected_all_res))
        self.assertSetEqual(set([repr(ea) for ea in expected_all_res]), set([repr(ea) for ea in all_res_by_classoffer]))

    def test_not_implemented_manager_most_recent_resource_per_classoffer(self):
        with self.assertRaises(NotImplementedError):
            ClassOffer.objects.most_recent_resource_per_classoffer()

    @skip("Not Implemented Feature")
    def test_manager_most_recent_resource_per_classoffer(self):
        from pprint import pprint
        sess = Session.objects.first()
        res_count = Resource.objects.count()
        expected_res = list(Resource.objects.all())
        expire = 0
        for lvl, display in Subject.LEVEL_CHOICES[:2]:
            for ver, _ in Subject.VERSION_CHOICES[:3]:
                avail = 0
                subj = Subject.objects.create(name='_'.join((lvl, ver)), level=lvl, version=ver)
                subj.save()
                res = Resource.objects.create(
                    content_type='text',
                    name='_'.join((lvl, ver, str(avail), str(expire))),
                    user_type=1,
                    avail=avail,
                    expire=expire,
                )
                res.save()
                res_count += 1
                subj.resources.add(res)
                co = ClassOffer.objects.create(subject=subj, session=sess, start_time=(time(17, 0)))
                co.save()
                while avail < sess.num_weeks:
                    avail += 1
                    res = Resource.objects.create(
                        content_type='text',
                        name='_'.join((lvl, ver, str(avail), str(expire))),
                        user_type=1,
                        avail=avail,
                        expire=expire,
                    )
                    res.save()
                    res_count += 1
                    subj.resources.add(res)
                expected_res.append(res)
        resource_count = Resource.objects.all().count()
        actual_res = ClassOffer.objects.most_recent_resource_per_classoffer().values('recent_resource')
        print("===================== most recent resource per classoffer ===============================")
        expected_names = [getattr(ea, 'name', '') for ea in expected_res]
        pprint(expected_names)
        print("------------------------------------------------------------------------")
        actual_names = [ea.get('recent_resource', '') for ea in actual_res]
        pprint(actual_names)
        # pprint([getattr(ea, 'recent_resource', '') for ea in actual_res.all()])
        self.assertLessEqual(sess.end_date, date.today())
        self.assertLessEqual(sess.end_date, dt.utcnow().date())
        self.assertEqual(res_count, resource_count)
        self.assertEqual(len(expected_res), len(actual_res))
        self.assertTrue(all(ea in expected_res for ea in actual_res))
        # self.assertSetEqual(set(expected_names), set(actual_names))

    def test_not_implemented_model_resources(self):
        first = ClassOffer.objects.first()
        with self.assertRaises(NotImplementedError):
            first.model_resources()

    @skip("Not Implemented Feature")
    def test_model_resources(self):
        model = ClassOffer.objects.first()
        subject = model.subject
        class_resource_count = model.resources.count()
        subj_resource_count = subject.resources.count()
        resources_count = Resource.objects.count()
        expected_resources = list(set(list(model.resources.all()) + list(subject.resources.all())))

        level_choice = Subject.LEVEL_CHOICES[1][0]
        level_choice = Subject.LEVEL_CHOICES[0][0] if level_choice == subject.level else level_choice
        version_choice = Subject.VERSION_CHOICES[0][0]
        other_subj = Subject.objects.create(level=level_choice, version=version_choice, name="other subject")
        other_model = ClassOffer.objects.create(subject=other_subj, session=model.session, start_time=time(17, 0))
        other_subj_res = Resource.objects.create(content_type='text', avail=0, expire=0, name="Other Subject Res")
        other_co_res = Resource.objects.create(content_type='text', avail=0, expire=0, name="Other ClassOffer Res")
        other_subj.resources.add(other_subj_res)
        other_model.resources.add(other_co_res)
        other_joined = list(other_subj.resources.all()) + list(other_model.resources.all())
        resources_count += 2

        subj_res = Resource.objects.create(content_type='text', avail=0, expire=0, name="Subject Res")
        co_res = Resource.objects.create(content_type='text', avail=0, expire=0, name="ClassOffer Res")
        subject.resources.add(subj_res)
        model.resources.add(co_res)
        expected_resources.extend([subj_res, co_res])
        actual_resources = model.model_resources(live=False).all()
        subj_resource_count += 1
        class_resource_count += 1
        resources_count += 2

        self.assertEqual(resources_count, Resource.objects.count())
        self.assertEqual(subj_resource_count, subject.resources.count())
        self.assertEqual(class_resource_count, model.resources.count())
        self.assertEqual(subj_resource_count + class_resource_count, len(actual_resources))
        self.assertTrue(all(ea in expected_resources for ea in actual_resources))
        self.assertTrue(all(ea in other_joined for ea in other_model.model_resources(live=False).all()))
        # self.assertSetEqual(set(expected_resources), set(actual_resources))
        # self.assertSetEqual(
        #     set(other_subj.resources.all() + other_model.resources.all()),
        #     set(other_model.model_resources(live=False).all())
        #     )

    def test_full_price(self):
        subject = Subject.objects.first()
        classoffer = ClassOffer.objects.first()
        full_price = subject.full_price

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertEqual(full_price, classoffer.full_price)

    def test_pre_discount(self):
        subject = Subject.objects.first()
        classoffer = ClassOffer.objects.first()
        pre_discount = subject.pre_pay_discount

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertEqual(pre_discount, classoffer.pre_discount)

    def test_multi_discount_reports_discount(self):
        subject = Subject.objects.first()
        classoffer = ClassOffer.objects.first()
        multi_discount = subject.multiple_purchase_discount

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertTrue(subject.qualifies_as_multi_class_discount)
        self.assertEqual(multi_discount, classoffer.multi_discount)

    def test_multi_discount_not_qualified(self):
        subject = Subject.objects.first()
        subject.qualifies_as_multi_class_discount = False
        subject.save()
        classoffer = ClassOffer.objects.first()

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertFalse(subject.qualifies_as_multi_class_discount)
        self.assertGreater(subject.multiple_purchase_discount, 0)
        self.assertEqual(classoffer.multi_discount, 0)

    def test_multi_discount_zero_discount(self):
        subject = Subject.objects.first()
        subject.multiple_purchase_discount = 0
        subject.save()
        classoffer = ClassOffer.objects.first()

        self.assertEqual(classoffer.subject_id, subject.id)
        self.assertTrue(subject.qualifies_as_multi_class_discount)
        self.assertEqual(subject.multiple_purchase_discount, 0)
        self.assertEqual(classoffer.multi_discount, 0)

    def test_pre_price(self):
        classoffer = ClassOffer.objects.first()
        self_computed = classoffer.full_price - classoffer.pre_discount
        subject = Subject.objects.first()
        subj_computed = subject.full_price - subject.pre_pay_discount

        self.assertEqual(self_computed, classoffer.pre_price)
        self.assertEqual(classoffer.subject, subject)
        self.assertEqual(subj_computed, classoffer.pre_price)

    def test_skip_week_explain(self):
        classoffer = ClassOffer.objects.first()
        expected_string = f"but you still get {classoffer.session.num_weeks} class days"
        self.assertEqual(expected_string, classoffer.skip_week_explain)

    def test_end_time(self):
        model = ClassOffer.objects.first()
        now = dt.now()
        start = dt(now.year, now.month, now.day, model.start_time.hour, model.start_time.minute)
        end = start + timedelta(minutes=model.subject.num_minutes)

        self.assertEqual(end.time(), model.end_time)

    def test_day_singular(self):
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()
        subject.num_weeks = 1
        subject.save()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]

        self.assertEqual(model.subject, subject)
        self.assertFalse(model.subject.num_weeks > 1)
        self.assertEqual(model.day, day)

    def test_day_plural(self):
        model = ClassOffer.objects.first()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]
        day = str(day) + 's'

        self.assertTrue(model.subject.num_weeks > 1)
        self.assertEqual(model.day, day)

    def test_day_short_singular(self):
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()
        subject.num_weeks = 1
        subject.save()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]
        day = day[:3]

        self.assertEqual(model.subject, subject)
        self.assertFalse(model.subject.num_weeks > 1)
        self.assertEqual(model.day_short, day)

    def test_day_short_plural(self):
        model = ClassOffer.objects.first()
        day = ClassOffer.DOW_CHOICES[model.class_day][1]
        day = day[:3]
        day += '(s)'

        self.assertTrue(model.subject.num_weeks > 1)
        self.assertEqual(model.day_short, day)

    def test_start_date_is_key_day(self):
        model = ClassOffer.objects.first()
        key_day = model.session.key_day_date
        key_day_of_week = key_day.weekday()
        if model.class_day != key_day_of_week:
            model.class_day = key_day_of_week
            model.save()

        self.assertEqual(model.class_day, key_day_of_week)
        self.assertEqual(model.start_date, model.session.key_day_date)

    def test_start_date_zero_max_shift(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = 0
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        if model.class_day != key_day_of_week:
            model.class_day = key_day_of_week
            model.save()

        self.assertEqual(model.session, session)
        self.assertEqual(session.max_day_shift, 0)
        self.assertEqual(model.class_day, key_day_of_week)
        self.assertEqual(model.start_date, session.key_day_date)

    def test_start_date_negative_shift(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = -2
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        date_shift = -1
        model.class_day = key_day_of_week + date_shift
        expected_date = session.key_day_date + timedelta(days=date_shift)
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.session, session)
        self.assertLess(session.max_day_shift, 0)
        self.assertNotEqual(model.class_day, key_day_of_week)
        self.assertNotEqual(date_shift, 0)
        self.assertEqual(model.start_date, expected_date)

    def test_start_date_positive_shift(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = 2
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        date_shift = 1
        model.class_day = key_day_of_week + date_shift
        result_date = session.key_day_date + timedelta(days=date_shift)
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.session, session)
        self.assertGreater(session.max_day_shift, 0)
        self.assertNotEqual(model.class_day, key_day_of_week)
        self.assertNotEqual(date_shift, 0)
        self.assertEqual(model.start_date, result_date)

    def test_start_date_out_of_negative_shift_range_opposite_direction(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = -2
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = 1
        result_date = session.key_day_date + timedelta(days=shift)
        target = key_day_of_week + shift
        if target > 6:
            target -= 7
        model.class_day = target
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.session, session)
        self.assertLess(session.max_day_shift, 0)
        self.assertNotEqual(model.class_day, key_day_of_week)
        self.assertEqual(model.start_date, result_date)

    def test_start_date_out_of_positive_shift_range_opposite_direction(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = 2
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = -1
        result_date = session.key_day_date + timedelta(days=shift)
        target_day = key_day_of_week + shift
        if target_day < 0:
            target_day += 7
        model.class_day = target_day
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.session, session)
        self.assertGreater(session.max_day_shift, 0)
        self.assertNotEqual(model.class_day, key_day_of_week)
        self.assertEqual(model.start_date, result_date)

    def test_start_date_beyond_negative_shift_range(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = -2
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = session.max_day_shift - 1
        result_date = session.key_day_date + timedelta(days=(shift + 7))
        target = key_day_of_week + shift
        if target < 0:
            target += 7
        model.class_day = target
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.session, session)
        self.assertLess(session.max_day_shift, 0)
        self.assertNotEqual(model.class_day, key_day_of_week)
        self.assertEqual(model.start_date, result_date)

    def test_start_date_beyond_positive_shift_range(self):
        model = ClassOffer.objects.first()
        session = Session.objects.first()  # expected to be connected to model
        session.max_day_shift = 2
        session.save()
        key_day_of_week = session.key_day_date.weekday()
        shift = session.max_day_shift + 1
        result_date = session.key_day_date + timedelta(days=(shift - 7))
        target = key_day_of_week + shift
        if target > 6:
            target -= 7
        model.class_day = target
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.session, session)
        self.assertEqual(session.max_day_shift, 2)
        self.assertEqual(shift, 3)
        self.assertNotEqual(model.class_day, key_day_of_week)
        self.assertEqual(model.start_date, result_date)

    def test_end_date_no_skips(self):
        subject = Subject.objects.first()  # expected to be connected to model
        session = Session.objects.first()  # expected to be connected to model
        session.skip_weeks = 0
        session.save()
        model = ClassOffer.objects.first()
        model.skip_weeks = 0
        expected = model.start_date + timedelta(days=7*(subject.num_weeks - 1))
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.subject, subject)
        self.assertEqual(model.session, session)
        self.assertEqual(session.skip_weeks, 0)
        self.assertEqual(model.skip_weeks, 0)
        self.assertEqual(model.end_date, expected)

    def test_end_date_skips_on_session_not_classoffer(self):
        subject = Subject.objects.first()  # expected to be connected to model
        session = Session.objects.first()  # expected to be connected to model
        session.skip_weeks = 1
        session.save()
        model = ClassOffer.objects.first()
        model.skip_weeks = 0
        expected = model.start_date + timedelta(days=7*(subject.num_weeks - 1))
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.subject, subject)
        self.assertEqual(model.session, session)
        self.assertGreater(session.skip_weeks, 0)
        self.assertEqual(model.skip_weeks, 0)
        self.assertEqual(model.end_date, expected)

    def test_end_date_with_skips(self):
        subject = Subject.objects.first()  # expected to be connected to model
        session = Session.objects.first()  # expected to be connected to model
        session.skip_weeks = 1
        session.save()
        model = ClassOffer.objects.first()
        model.skip_weeks = 1
        expected = model.start_date + timedelta(days=7*(subject.num_weeks + model.skip_weeks - 1))
        model.save()
        model = ClassOffer.objects.first()

        self.assertEqual(model.subject, subject)
        self.assertEqual(model.session, session)
        self.assertGreater(session.skip_weeks, 0)
        self.assertGreater(model.skip_weeks, 0)
        self.assertEqual(model.end_date, expected)

    def test_num_level(self):
        model = ClassOffer.objects.first()
        expected = model._num_level
        self.assertEqual(expected, model.num_level)

    def test_set_num_level_subject_level_bad_value(self):
        level_dict = Subject.LEVEL_ORDER
        higher = 100 + max(level_dict.values())
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()  # expected to be connected to model
        original = model.num_level
        subj_level, i = '', 0
        while subj_level in level_dict or subj_level == subject.level or level_dict.get(subj_level, '') == original:
            subj_level = Subject.LEVEL_CHOICES[i][0]
            i += 1
        subject.level = subj_level
        subject.save()
        expected = higher
        model.set_num_level()

        self.assertEqual(model.subject, subject)
        self.assertNotEqual(model.num_level, original)
        self.assertEqual(model.num_level, expected)

    def test_set_num_level_correct(self):
        level_dict = Subject.LEVEL_ORDER
        model = ClassOffer.objects.first()
        subject = Subject.objects.first()  # expected to be connected to model
        original = model.num_level
        subj_level, i = '', 0
        while subj_level not in level_dict or subj_level == subject.level or level_dict[subj_level] == original:
            subj_level = Subject.LEVEL_CHOICES[i][0]
            i += 1
        subject.level = subj_level
        subject.save()
        expected = level_dict.get(subj_level, None)
        model.set_num_level()

        self.assertEqual(model.subject, subject)
        self.assertNotEqual(model.num_level, original)
        self.assertEqual(model.num_level, expected)


class SessionModelTests(SimpleModelTests, TestCase):
    Model = Session
    detail_url_name = 'classoffer_display_session'
    detail_admin_url_name = 'checkin_session'
    repr_dict = {'Session': 'name'}
    str_list = ['name']
    defaults = {'name': "test_model"}

    def test_get_absolute_url(self, url_field='__str__'):
        super().test_get_absolute_url(url_field=url_field)

    def test_get_admin_absolute_url(self, url_field='__str__'):
        from django.urls import reverse

        fields = self.get_field_info()
        model = self.create_model(create_method_name=self.create_method_name, **fields)
        if self.detail_admin_url_name is None:
            with self.assertRaises(AttributeError):
                url = model.get_admin_absolute_url()
            return
        url = model.get_admin_absolute_url()
        arg = getattr(model, url_field, None)
        arg = arg() if callable(arg) else arg
        expected = reverse(self.detail_admin_url_name, args=[arg])
        self.assertEqual(url, expected)


class SessionCoverageTests(TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_hidden.json']

    def create_session(self, **kwargs):
        obj = Session.objects.create(**kwargs)
        # obj.refresh_from_db()
        return obj

    def test_default_date_error_on_wrong_fields(self):
        session = Session.objects.get(id=1)
        with self.assertRaises(ValueError):
            session._default_date('expire_date')

    def test_default_date_traverse_prev_for_final_session(self):
        first = Session.objects.first()  # key_day_date = "2020-04-30", num_weeks = 5
        minimum_session_weeks = settings.SESSION_LOW_WEEKS
        second = self.create_session(name="short_session", num_weeks=(minimum_session_weeks - 1))
        second.save()
        expected_key_day = first.key_day_date + timedelta(days=7*(first.num_weeks + first.break_weeks))
        third = self.create_session(name="third_test")
        third.save()

        self.assertGreater(minimum_session_weeks, 1)  # Otherwise we probably have error on create of second.
        self.assertEqual(first.skip_weeks, 0)  # Therefore, expected_key_day should be correct.
        self.assertGreater(third.start_date, first.end_date)
        self.assertEqual(third.publish_date, first.expire_date)
        self.assertEqual(expected_key_day, third.key_day_date)

    def test_compute_expire_day_with_key_day_none(self):
        session = Session.objects.get(id=1)
        computed_expire = session.computed_expire_day()
        self.assertEqual(session.expire_date, computed_expire)

    def test_clean_determine_date_from_previous(self):
        first = Session.objects.first()  # key_day_date = "2020-04-30", num_weeks = 5
        second = self.create_session(name="second_test")
        second.save()
        first_key_day = first.key_day_date  # 2020-04-30
        collide_key_day = first_key_day + timedelta(days=7*(first.num_weeks - 1))
        third = self.create_session(name="third_test", key_day_date=collide_key_day)
        third.save(with_clean=True)

        self.assertGreater(first.num_weeks, 1)
        self.assertGreater(third.start_date, second.end_date)
        self.assertGreater(second.start_date, first.end_date)

    def test_repr(self):
        session = Session.objects.first()
        repr_string = f"<Session: {session.name} >"
        self.assertEqual(repr_string, repr(session))

    def test_create_no_default_functions_no_shift(self):
        """ Session.create works with defined 'key_day_date' and 'publish_date'. """
        key_day = date.today() - timedelta(days=1)
        day_adjust, duration = 0, 5
        publish = key_day - timedelta(days=7*(duration - 1)+1)
        expire = key_day + timedelta(days=8)
        sess = self.create_session(
            name='t1_no_shift',
            key_day_date=key_day,
            max_day_shift=day_adjust,
            num_weeks=duration,
            publish_date=publish,
        )
        self.assertTrue(isinstance(sess, Session))
        self.assertEqual(sess.__str__(), sess.name)
        self.assertEqual(sess.start_date, sess.key_day_date)
        self.assertEqual(sess.publish_date, publish)
        self.assertEqual(sess.expire_date, expire)
        self.assertEqual(sess.end_date, key_day + timedelta(days=7*(duration - 1)))

    def test_session_defaults_on_creation(self):
        """ Session.create works with the date default functions in the model. """
        day_adjust, duration = 0, 5
        first = Session.objects.first()
        key_day = first.key_day_date + timedelta(days=7*(first.num_weeks + first.skip_weeks))
        new_publish_date = first.expire_date
        expire = key_day + timedelta(days=8)
        end = key_day + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t2_no_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEqual(sess.key_day_date, key_day)
        self.assertEqual(sess.start_date, key_day)
        self.assertEqual(sess.publish_date, new_publish_date)
        self.assertEqual(sess.expire_date, expire)
        self.assertEqual(sess.end_date, end)
        self.assertEqual(sess.prev_session.name, first.name)
        self.assertEqual(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)

    def test_create_early_shift_no_skip(self):
        """ Sessions with negative 'max_day_shift' correctly compute their dates. """
        first = Session.objects.first()
        day_adjust, duration = first.max_day_shift, first.num_weeks
        key_day = first.key_day_date + timedelta(days=7*duration)
        publish = first.expire_date
        expire = key_day + timedelta(days=8)
        start = key_day + timedelta(days=day_adjust)
        end = key_day + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t1_early_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEqual(sess.key_day_date, key_day)
        self.assertEqual(sess.publish_date, publish)
        self.assertEqual(sess.expire_date, expire)
        self.assertEqual(sess.start_date, start)
        self.assertEqual(sess.start_date, sess.key_day_date + timedelta(days=day_adjust))
        self.assertEqual(sess.end_date, end)
        self.assertEqual(sess.prev_session.expire_date, sess.publish_date)
        self.assertLess(sess.prev_session.end_date, sess.start_date)

    def test_dates_late_shift_no_skip(self):
        """ Sessions with positive 'max_day_shift' correctly compute their dates. """
        first = Session.objects.first()
        day_adjust, duration = 5, first.num_weeks
        key_day = first.key_day_date + timedelta(days=7*duration)
        publish = first.expire_date
        expire = key_day + timedelta(days=8+day_adjust)
        start = key_day
        end = key_day + timedelta(days=7*(duration - 1)+day_adjust)
        initial_end = first.key_day_date + timedelta(days=7*(duration - 1))
        sess = self.create_session(
            name='t1_late_shift',
            max_day_shift=day_adjust,
            num_weeks=duration,
        )
        self.assertEqual(sess.key_day_date, key_day)
        self.assertEqual(sess.publish_date, publish)
        self.assertEqual(sess.expire_date, expire)
        self.assertEqual(sess.start_date, start)
        self.assertEqual(sess.end_date, end)
        self.assertLess(sess.prev_session.end_date, sess.start_date)
        self.assertEqual(sess.prev_session.end_date, initial_end)


# end test_instruction_models.py
