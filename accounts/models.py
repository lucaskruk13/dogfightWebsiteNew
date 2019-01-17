from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg
from django.core.validators import RegexValidator
from feed.models import Course, Dogfight
from datetime import datetime
from django.utils import timezone
import re


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    print (type(instance))
    return 'user_{0}/profile/{1}.jpg'.format(instance.user.id, timezone.now())

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    handicap = models.CharField(max_length=6, null=False, blank=False,default=0, validators=[
        RegexValidator(
            regex="^[+]?\d*\.?\d*$",
            message="Invalid Handicap",
            code='invalid_handicap'
        )
    ])
    initial = models.BooleanField(default=True) # Initial Value to update the handicap
    profile_image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)



    def getCurrentQuota(self):
        avg = Scores.objects.filter(user=self.user, countable=True).order_by('-created_at')[:5].aggregate(Avg('score'))
        if avg['score__avg']:
            return avg['score__avg']



    def getHandicap(self):
        return float(self.handicap)

    def fullname(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def __str__(self):
        return "{} | {}, {}".format(self.user.username, self.user.last_name, self.user.first_name)

    def getRoundedQuota(self):
        quota = self.getCurrentQuota()

        if quota is None:
            return None
        return round(self.getCurrentQuota())




class Scores(models.Model):
    user = models.ForeignKey(User, related_name='scores', on_delete=models.CASCADE) # Every Score has a profile
    dogfight = models.ForeignKey(Dogfight, related_name='scores_dogfight', on_delete=models.CASCADE, default=1) # Every Score has a course
    score = models.IntegerField(default=0, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    countable = models.BooleanField(default=False) # Whenever we sign up it will create a new default score, but we cannot count that in the quota





# TODO: Fix scores so it updates the countable flag upon save
def on_scores_save(sender, instance, **kwargs):

    if instance.score >0:
        instance.countable = True;

    return instance

def on_profile_save(sender, instance, **kwargs):

    scoresCount = Scores.objects.filter(user=instance.user).count()
    handicap = instance.handicap

    # if there are no scores, but the Initial Value is false, let's add the baseline scores
    # The initial value is changed by the view's is form_valid method
    if ((not instance.initial) and (scoresCount == 0)):
        for i in range(5):
            score = Scores()
            score.user = instance.user # Instance is of class Profile
            score.score = generateInitialQuota(instance.handicap)
            score.dogfight = Dogfight.objects.first()
            score.countable = True
            score.save()

post_save.connect(on_profile_save, sender=Profile) # Links Scores saving function to the function on_profile_save
post_save.connect(on_scores_save, sender=Scores) # Links on_scores_saved to be called when scores are saved.

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def generateInitialQuota(handicap):

    # when we get here, the handicap should be valid
    # if the handicap is + we need to convert it to - to add to 36
    handicap = float(re.sub(r"[+]", "-", handicap))

    return round(36.0 - handicap)





