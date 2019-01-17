from feed.views import CourseView
from feed.models import Course
from django.test import TestCase
from django.urls import reverse, resolve

class CourseViewTests(TestCase):

    fixtures = ['course_fixture.json']


    def setUp(self):
        self.course = Course.objects.first()

        self.url = reverse('course', kwargs={'pk': self.course.pk})
        self.response = self.client.get(self.url)

    def test_course_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_course_url_resolves_course_view(self):
        view = resolve('/course/1/')
        self.assertEquals(view.func.view_class, CourseView)
