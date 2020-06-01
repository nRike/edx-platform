"""
Tests for Dates Tab API in the Course Home API
"""


import ddt

from django.urls import reverse

from course_modes.models import CourseMode
from lms.djangoapps.course_home_api.tests.utils import BaseCourseHomeTests
from lms.djangoapps.course_home_api.toggles import COURSE_HOME_MICROFRONTEND, COURSE_HOME_MICROFRONTEND_DATES_TAB
from student.models import CourseEnrollment


@ddt.ddt
class DatesTabTestViews(BaseCourseHomeTests):
    """
    Tests for the Dates Tab API
    """
    @classmethod
    def setUpClass(cls):
        BaseCourseHomeTests.setUpClass()
        cls.url = reverse('course-home-dates-tab', args=[cls.course.id])

    @COURSE_HOME_MICROFRONTEND.override(active=True)
    @COURSE_HOME_MICROFRONTEND_DATES_TAB.override(active=True)
    @ddt.data(CourseMode.AUDIT, CourseMode.VERIFIED)
    def test_get_authenticated_enrolled_user(self, enrollment_mode):
        CourseEnrollment.enroll(self.user, self.course.id, enrollment_mode)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Pulling out the date blocks to check learner has access.
        date_blocks = response.data.get('course_date_blocks')
        self.assertEqual(response.data.get('learner_is_verified'), enrollment_mode == CourseMode.VERIFIED)
        self.assertTrue(all(block.get('learner_has_access') for block in date_blocks))

    @COURSE_HOME_MICROFRONTEND.override(active=True)
    @COURSE_HOME_MICROFRONTEND_DATES_TAB.override(active=True)
    def test_get_authenticated_user_not_enrolled(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data.get('learner_is_verified'))

    def test_get_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @COURSE_HOME_MICROFRONTEND.override(active=True)
    @COURSE_HOME_MICROFRONTEND_DATES_TAB.override(active=True)
    def test_get_unknown_course(self):
        url = reverse('course-home-dates-tab', args=['course-v1:unknown+course+2T2020'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
