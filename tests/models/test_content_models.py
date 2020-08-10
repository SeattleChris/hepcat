from django.test import TestCase, TransactionTestCase
from unittest import skip
from .helper_models import SimpleModelTests, SiteContent, Location, Resource, Student, ClassOffer
# , UserHC, Session, Subject
# Create your tests here.


class SiteContentModelTests(SimpleModelTests, TestCase):
    Model = SiteContent
    repr_dict = {'SiteContent': 'name'}


class LocationModelTests(SimpleModelTests, TestCase):
    Model = Location
    repr_dict = {'Location': 'name', 'Link': 'map_link'}


class ResourceModelTests(SimpleModelTests, TransactionTestCase):
    fixtures = ['tests/fixtures/db_basic.json', 'tests/fixtures/db_hidden.json']
    Model = Resource
    repr_dict = {'Resource': 'title', 'Type': 'content_type'}
    str_list = ['title', ]
    ProfileStudent = Student

    # Setup for publish method
    # Need a student user & profile
    # ? Need a Location
    # Need a Session, Subject, and ClassOffer
    # The student needs to be associated with the ClassOffer
    # Need Resource(s) attached to a Subject or ClassOffer
    # - Can't view before joining
    # - Immediately available once joined
    # - Not yet published
    # - Already expired
    # # # #
    # Have
    # resource = Resource.objects.get(id=1) has .title = "Congrats on Finishing class!"
    # resource is connected to a Subject with id=1 and a ClassOffer with id=1
    # classoffer = ClassOffer.objects.get(id=1) is connected to resource and a Session, Subject, Location.
    # there is a student with id=1, and they have a registration for this classoffer.

    def test_manager_live_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            Resource.objects.live()

    @skip("Not Implemented")
    def test_publish_not_view_if_not_joined(self):
        """ For a User NOT signed in a ClassOffer, determine they are NOT allowed to see an associated Resource. """
        student = self.ProfileStudent.objects.first()
        classoffer = ClassOffer.objects.get(id=1)
        # classoffer settings - 'key_day_date': '2020-04-30', 'num_weeks': 5 ==> class ended already.
        resource = Resource.objects.get(id=1)
        # resource has fields - user_type: 1 (student), avail: 200 (after finished), expire: 0 (never)
        available = resource.publish(classoffer)

        self.assertGreater(len(student.taken), 0)
        self.assertIn(classoffer, student.taken)
        self.assertIn(student, classoffer.students)
        self.assertEquals(resource.classoffer, classoffer)
        self.assertIn(resource, classoffer.resource_set)
        self.assertFalse(available)

    @skip("Not Implemented")
    def test_publish_can_view_avail_is_immediate(self):
        """ For a User signed in a ClassOffer, determine they are allowed to see an associated immediate Resource. """
        pass

    @skip("Not Implemented")
    def test_publish_can_view_during_published(self):
        """ For a User signed in a ClassOffer, determine they are allowed to see a currently published Resource. """
        pass

    @skip("Not Implemented")
    def test_publish_can_view_never_expired(self):
        """ For a User signed in a ClassOffer, determine they can view an associated never expired Resource. """
        print("=========================== ResourceModelTests - Running Here ========================================")
        student = self.ProfileStudent.objects.first()
        classoffer = ClassOffer.objects.get(id=1)
        # classoffer settings - 'key_day_date': '2020-04-30', 'num_weeks': 5 ==> class ended already.
        resource = Resource.objects.get(id=1)
        # resource has fields - user_type: 1 (student), avail: 200 (after finished), expire: 0 (never)
        available = resource.publish(classoffer)

        self.assertGreater(len(student.taken), 0)
        self.assertIn(classoffer, student.taken)
        self.assertEquals(resource.classoffer, classoffer)
        self.assertIn(student, classoffer.students)
        self.assertIn(resource, classoffer.resource_set)
        self.assertTrue(available)

    @skip("Not Implemented")
    def test_publish_not_view_before_publish(self):
        """ For a User signed in a ClassOffer, determine they do NOT see an associated Resource early. """
        pass

    @skip("Not Implemented")
    def test_publish_not_view_after_expired(self):
        """ For a User signed in a ClassOffer, they do NOT see an associated expired Resource. """
        pass


# end of test.py file
