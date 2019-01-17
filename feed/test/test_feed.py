from feed.views import FeedView, CourseView
from django.test import TestCase
from django.urls import reverse, resolve
from feed.models import Course, Dogfight
from accounts.models import Profile, Scores

from django.utils import timezone
from django.contrib.auth.models import User


class FeedTest(TestCase):

    fixtures = ['course_fixture'] # Load Courses to every test case becuase it's non related data

    @classmethod
    def setUpClass(cls):
        super(FeedTest, cls).setUpClass()

        cls.url = reverse('feed')


    def setUp(self):
        self.feedResponse = self.client.get(self.url)
        self.feedView = resolve('/')

class AuthenticatedFeedTest(FeedTest):

    fixtures = ['course_fixture', 'initial_Dogfight']

    @classmethod
    def setUpClass(cls):
        super(AuthenticatedFeedTest, cls).setUpClass()

        # Create the First User
        cls.username = 'johnappleseed'
        cls.password = 'secret123'

        cls.user = User.objects.create(first_name='John', last_name='Appleseed', email='john@appleseed.com',
                                       username=cls.username)
        cls.user.set_password(cls.password)

        cls.user.save()

        profile = cls.user.profile
        profile.handicap = "5"
        profile.bio = "Its Me"
        profile.initial = False
        profile.save()


        # Create a Dogfight
        cls.dogfight = Dogfight.objects.create(course=Course.objects.first())

        # Access signup after setup so we have access to the User who is authenticated
        cls.dogfightSignupURL = reverse('dogfight_signup',
                                         kwargs={"dogfight_pk": cls.dogfight.pk,
                                                 "user_pk": cls.user.pk})  # Get the signup url

    def setUp(self):


        # Log the User In
        self.client.login(username=self.username, password=self.password)

        super().setUp()

class TestDogfightNotSetup(FeedTest):


    @classmethod
    def setUpTestData(cls):
        # Create a dogfight with a date in the past. This will simulate no currnet dogfight availible.
        startdate = timezone.now() - timezone.timedelta(days=5)
        Dogfight.objects.create(date=startdate, course=Course.objects.first())

    def test_feed_status_code(self):
        self.assertTrue(Dogfight.objects.exists()) # Make Sure Dogfight Was Created
        self.assertEquals(self.feedResponse.status_code, 200)

    def test_feed_url_resolves_feed_view(self):
        self.assertEquals(self.feedView.func.view_class, FeedView)

    def test_no_dogfight_present(self):
        # If No Dogfight is present, then the parallax window will not show
        self.assertNotContains(self.feedResponse, 'class="parallax-window"')

class TestWithDogfightSetup(FeedTest):

    fixtures = ['initial_data','course_fixture']

    @classmethod
    def setUpTestData(cls):

        # Create a dogfight, defaulting logic should allow it to be picked up by the feed.
        dogfight = Dogfight.objects.create(course=Course.objects.first())
        Scores.objects.create(user=User.objects.first(), dogfight=dogfight)


    def test_feed_status_code(self):
        self.assertEquals(self.feedResponse.status_code, 200)

    def test_dogfight_present(self):

        # If a dogfight is available, then the parallax window will show
        self.assertContains(self.feedResponse, 'class="parallax-window"')
        self.assertContains(self.feedResponse, 'feed-table') # referencing the Table ID

    def test_prize_money_table_exits(self):
        self.assertContains(self.feedResponse, 'prize-money-card')

    def test_prize_money_number_of_places(self):
        # The Initial Data only contains 5 places, so the size should be 1, which returns a class of prize-money-unavailible
        self.assertContains(self.feedResponse, 'prize-money-unavailible')


class TestNoSignups(FeedTest):

    def test_no_signup_table_present(self):
        self.assertNotContains(self.feedResponse, 'feed-table-container')

    def test_no_waiting_list_table_present(self):
        self.assertNotContains(self.feedResponse, 'waiting-list-table-card')

class TestMultipleDogfightsUpcoming(FeedTest):

    @classmethod
    def setUpTestData(cls):
        # Create a dogfight with a date in the past. This will simulate no currnet dogfight availible.

        startdate = timezone.now() + timezone.timedelta(days=2)
        extendedStartTime = timezone.now() + timezone.timedelta(days=8)
        farOffStartTime = timezone.now() + timezone.timedelta(days=15)


        Dogfight.objects.create(date=extendedStartTime, course=Course.objects.first()) # Next Weeks Dogfight
        Dogfight.objects.create(date=farOffStartTime, course=Course.objects.last()) # Week After
        Dogfight.objects.create(date=startdate, course=Course.objects.last())  # Upcoming in the future


    def test_the_upcoming_dogfight(self):
        currentDogfight = self.feedResponse.context.get('dogfight')
        self.assertTrue(currentDogfight.date, timezone.now() + timezone.timedelta(days=2))

        self.assertTrue(currentDogfight.course, Course.objects.first())

class TestFeedPageNoUserLoggedIn(FeedTest):


    @classmethod
    def setUpTestData(cls):
        # Create a dogfight
        Dogfight.objects.create(course=Course.objects.first())

    def test_the_user_is_authenticated(self):
        user = self.feedResponse.context.get('user')
        self.assertFalse(user.is_authenticated) # No User Should Be Logged In

    def test_no_signup_button_present(self):

        # Feed Should not have signup buttons for the dogfight
        self.assertNotContains(self.feedResponse, 'dogfight-signup-button')
        self.assertNotContains(self.feedResponse, 'dogfight-signup-cancel-button')

    def test_login_and_signup_are_present_in_navigation(self):
        self.assertContains(self.feedResponse, 'login')
        self.assertContains(self.feedResponse, 'logout')

class TestFeedPageUserLoggedIn(AuthenticatedFeedTest):

    def setUp(self):
        super().setUp()

        self.dogfightSignupRequest = self.client.get(self.dogfightSignupURL)

    def test_user_is_logged_in(self):
        self.assertTrue(self.user.is_authenticated)

    def test_signup_button_appears(self):

        self.assertContains(self.feedResponse, 'dogfight-signup-button')

    def test_signup_for_upcoming_dogfight(self):

        self.assertRedirects(self.dogfightSignupRequest, self.url) # should redirect to home page

        self.assertTrue(Scores.objects.filter(dogfight=self.dogfight, user=self.user).exists()) # New Score for this Dogfight should be created


class TestFeedPageUserAlreadySignedUp(AuthenticatedFeedTest):

    def setUp(self):
        # Create a Score object before signin so the request picks it up
        Scores.objects.create(dogfight=self.dogfight, user=self.user)

        super().setUp()

        # Create a request to the cancel button
        cancelSignupURL = reverse('cancel_dogfight_signup', kwargs={'dogfight_pk': self.dogfight.pk, 'user_pk':self.user.pk})
        self.cancelRequest = self.client.get(cancelSignupURL)

        self.feedResponseAfterCancel = self.client.get(self.url)

    def test_cancel_button_appears(self):
        self.assertContains(self.feedResponse, 'dogfight-signup-cancel-button')

    def test_cancel_redirects_to_feed(self):
        self.assertRedirects(self.cancelRequest, self.url) # Should return to the home page

    def test_signup_button_returns(self):
        self.assertContains(self.feedResponseAfterCancel, 'dogfight-signup-button')

    def test_score_was_destroyed(self):
        self.assertFalse(Scores.objects.filter(dogfight=self.dogfight, user=self.user).exists())

class TestWaitingListTableExists(FeedTest):

    @classmethod
    def setUpTestData(cls):

        # Create a dogfight with 4 groups
        cls.dogfight = Dogfight.objects.create(course=Course.objects.first(), number_of_groups=4)

        # Create Users & scores for this dogfight

        for i in range(0, 20):
            user = User.objects.create(username="test{}".format(i))
            Scores.objects.create(dogfight=cls.dogfight, user=user, score=30)

    def test_waiting_list_is_present(self):
        self.assertContains(self.feedResponse, "waiting-list-table-card")

    def test_waiting_list_contains_four_rows(self):
        self.assertContains(self.feedResponse, 'waiting-list-row', 4)

    def test_prize_money_availible(self):
        # if the prize money is present, it should return a table row class of prize-money-availible
        self.assertContains(self.feedResponse, 'prize-money-availible')