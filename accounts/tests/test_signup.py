from django.test import TestCase
from django.urls import reverse, resolve
from accounts.views import signup
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Profile, Scores
from accounts.forms import ProfileForm
from django.core import management

class SignUpTest(TestCase):

    # Dont Import Auth Data Fixture as Test Cases Create accounts and they can create a PK Collision.
    fixtures = ['initial_feed.json']


    @classmethod
    def setUpClass(cls):
        super(SignUpTest, cls).setUpClass() # Have the superclass setup

        # Class Level URLs
        cls.signup_url = reverse('signup')
        cls.my_account_url = reverse('my_account')
        cls.feed_url = reverse('feed')

        cls.signupView = resolve('/signup/')


        cls.signupData = {
            'username':'john',
            'email':'john@appleseed.com',
            'first_name':'john',
            'last_name':'appleseed',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456',

        }

        cls.profileData = {
            'handicap': '1',
            'bio': 'Its Me!',
        }


    def setUp(self):
        self.signupResponse = self.client.get(self.signup_url)
        self.signupPost = self.client.post(self.signup_url, self.signupData)

        self.profileResponse = self.client.get(self.my_account_url)
        self.profilePost = self.client.post(self.my_account_url, self.profileData)

        self.feedResponse = self.client.get(self.feed_url)

class SignupPageSuccessfulTests(SignUpTest):

    def test_status_code(self):
        self.assertEquals(self.signupResponse.status_code, 200)

    def test_signup_resolves_signup_view(self):
        self.assertEquals(self.signupView.func, signup)

    def test_csrf(self):
        self.assertContains(self.signupResponse, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.signupResponse.context.get('form')
        self.assertIsInstance(form, UserCreationForm)

    def test_redirection(self):

        # A Valid submission from the signup page will redirect to the account page
        # A Valid submission from the profile page will redirect to the feed

        self.assertRedirects(self.signupPost, self.my_account_url)
        self.assertRedirects(self.profilePost, self.feed_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_profile_updated(self):
        user = User.objects.first()
        profile = Profile.objects.get(user=user)

        self.assertEquals(profile.bio, "Its Me!")

    def test_scores_were_created(self):

        self.assertTrue(Scores.objects.exists()) # Scores should be created
        self.assertEquals(Scores.objects.all().count(), 5) # Five total scores should be created

        score = Scores.objects.first()
        self.assertEquals(score.score, 35) # Test quota was created successfully

    def test_user_authentication(self):
        user = self.feedResponse.context.get('user')
        self.assertTrue(user.is_authenticated)

class SignupPageInvalidSubmission(SignUpTest):


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.signupData = {
            'username': 'john',
            'email': 'john@appleseed..com',
            'first_name': 'john',
            'last_name': 'appleseed',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456',

        }

    def test_signup_status_code(self):
        self.assertEquals(self.signupPost.status_code, 200)

    def test_form_errors(self):
        form = self.signupPost.context.get('form')
        self.assertTrue(form.errors)

    def test_user_not_created(self):
        self.assertFalse(User.objects.exists())

class ProfilePageInvalidSubmission(SignUpTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.profileData = {
            'handicap': '2..5',
            'bio': 'its me',
         }

    def setUp(self):
        super().setUp()

        self.form = self.profilePost.context.get('form')

    def test_account_status_code(self):
        # Invalid submission should not redirect
        self.assertEquals(self.profilePost.status_code, 200)


    def test_csrf(self):
        self.assertContains(self.profilePost, 'csrfmiddlewaretoken')

    def test_contains_form(self):

        self.assertIsInstance(self.form, ProfileForm)

    def test_form_contains_errors(self):
        self.assertTrue(self.form.errors)

    def test_scores_were_not_created(self):
        self.assertFalse(Scores.objects.exists())

class ProfilePageInvalidSumbissionNegativeHandicap(SignUpTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.profileData = {
            'handicap': '-2.5',
            'bio': 'its me',
        }

    def setUp(self):
        super().setUp()

        self.form = self.profilePost.context.get('form')

    def test_form_contains_errors(self):
        self.assertTrue(self.form.errors)

    def test_scores_were_not_created(self):
        self.assertFalse(Scores.objects.exists())

class ProfilePageValidSubmissionPlusHandicapNumber(SignUpTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.profileData = {
            'handicap': '+2.5',
            'bio': 'its me',
        }

    def test_scores_were_created_successfully(self):
        self.assertEquals(Scores.objects.count(), 5) # 5 Scores Should Be Created

        score = Scores.objects.first()
        self.assertEquals(score.score, 38) # Test Quota Created Successfully.