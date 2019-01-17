from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView
from accounts.models import Scores
from feed.models import Course, Dogfight
from datetime import datetime
from django.contrib.auth.models import User

from django.contrib import messages

class FeedView(TemplateView):
    template_name = 'feed/feed.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation to get a context
        context = super().get_context_data(**kwargs)

        dogfight = get_current_dogfight()
        scores = get_scores_list()
        # Add in a QuerySet of all the Courses
        context['course_list'] = Course.objects.all()
        context['dogfight'] = dogfight
        context['scores_list'] = scores
        context['signed_up'] = is_signed_up(self.request.user, dogfight)
        context['waiting_list'] =get_waiting_list()

        # If Nobody is signed up, the prize money dictionary cant populate based on scores. THe Model is capable of handeling the right amount of players, but we need to ensure we are not passing it a empty set
        if scores is not None and scores.count():
            context['prize_money_dict'] = dogfight.get_prize_money_dictionary_for_num_players(scores.count())
        else:
            context['prize_money_dict'] = {"Not Enough Players": "No Players Currently Signed Up"}

        context['golfer_list'] = User.objects.all()


        return context

class CourseView(DetailView):
    model = Course
    context_object_name = 'course'
    template_name = 'feed/course.html'

# Creating a url to sign up the golfer
def dogfight_signup(request, dogfight_pk, user_pk):

    user = request.user # Get the requesting User
    dogfight = get_current_dogfight() # Get the Current User

    score = Scores.objects.create(user=user, dogfight=dogfight) # Create the Score Object, Thus, singing them up

    if score:
        messages.success(request, 'Sign Up Successful!')

    return redirect('feed') # Redirect to the Feed becuase we have nothing else to show them.


def cancel_dogfight_signup(request, dogfight_pk, user_pk):

    user = request.user
    dogfight = get_current_dogfight()

    Scores.objects.filter(user=user, dogfight=dogfight).delete()

    if not Scores.objects.filter(user=user, dogfight=dogfight).count():
        messages.info(request, 'Successfully Removed from this weeks Dogfight')

    return redirect('feed')

def is_signed_up(user, dogfight):
    # Get All The user Scores

    if not user.is_anonymous and dogfight:

        # check to see if this dogfight is in the user scores. If the count is greater than 0 then we know they are signed up
        if Scores.objects.filter(user=user, dogfight=dogfight).count():
            return True

    return False



def get_scores_list():
    dogfight = get_current_dogfight()

    # If there is no dogfight, there is no need to retrieve the Scores
    if dogfight is None:
        return None

    scores = Scores.objects.filter(dogfight=dogfight).order_by('created_at')

    if dogfight.number_of_groups is None:
        return scores
    else:
        return scores[:(dogfight.number_of_groups*4)]

def get_waiting_list():
    dogfight= get_current_dogfight()

    # If there is no dogfight, there is no need to retrieve the Scores
    if dogfight is None:
        return None

    scores= Scores.objects.filter(dogfight=dogfight).order_by('created_at')

    if dogfight.number_of_groups is None:
        return None
    else:
       return scores[(dogfight.number_of_groups*4):]


def get_current_dogfight():

    dogfight = Dogfight.objects.filter(date__gte=datetime.now()).order_by('date').first() # Gets the upcoming dogfight, even if there are dogfights scheduled for a later date
    return dogfight

