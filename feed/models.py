from django.db import models
from django.utils import timezone
from datetime import datetime,timedelta, time
from django.contrib.auth.models import User


def get_next_weekday(startdate, weekday):
    """
    @startdate: given date, in format '2013-05-25'
    @weekday: week day as a integer, between 0 (Monday) to 6 (Sunday)
    """
    d = datetime.strptime(startdate, '%Y-%m-%d')
    t = timedelta((7 + weekday - d.weekday()) % 7)
    return (d + t).strftime('%Y-%m-%d')


class Course(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.CharField(max_length=4000, blank=True, null=True)
    location = models.CharField(max_length=50, blank=False, null=False)
    par = models.IntegerField(blank=False, null=False)
    yardage = models.CharField(blank=False, null=False, max_length=140)
    img = models.CharField(blank=True, null=True, max_length=50)


    def __str__(self):
        return "{} - {}".format(self.name, self.location)


class Dogfight(models.Model):

    date = models.DateField(default=get_next_weekday(timezone.now().strftime('%Y-%m-%d'), 5), blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False, default=time(hour=7, minute=30))
    number_of_groups = models.IntegerField(blank=False, null=False, default=5)
    course = models.ForeignKey(Course, related_name='dogfight_course', on_delete=models.CASCADE)

    # Create the prize money Dictionary, since there is no specific patter or percentage, we have to do it the hard way
    prizeMoneyDict = {}
    prizeMoneyDict[6] = {1: 50, 2: 30}
    prizeMoneyDict[7] = {1: 50, 2: 30, 3: 15}
    prizeMoneyDict[8] = {1: 55, 2: 35, 3: 20}
    prizeMoneyDict[9] = {1: 60, 2: 40, 3: 25}
    prizeMoneyDict[10] = {1: 60, 2: 40, 3: 25, 4: 15}
    prizeMoneyDict[11] = {1: 60, 2: 45, 3: 30, 4: 20}
    prizeMoneyDict[12] = {1: 65, 2: 45, 3: 35, 4: 25}
    prizeMoneyDict[13] = {1: 65, 2: 45, 3: 35, 4: 25, 5: 15}
    prizeMoneyDict[14] = {1: 70, 2: 50, 3: 35, 4: 25, 5: 20}
    prizeMoneyDict[15] = {1: 70, 2: 55, 3: 40, 4: 30, 5: 20}
    prizeMoneyDict[16] = {1: 75, 2: 55, 3: 45, 4: 35, 5: 20}
    prizeMoneyDict[17] = {1: 80, 2: 60, 3: 50, 4: 35, 5: 20}
    prizeMoneyDict[18] = {1: 80, 2: 60, 3: 55, 4: 40, 5: 25}
    prizeMoneyDict[19] = {1: 80, 2: 60, 3: 55, 4: 40, 5: 25, 6: 15}
    prizeMoneyDict[20] = {1: 85, 2: 65, 3: 55, 4: 40, 5: 25, 6: 20}
    prizeMoneyDict[21] = {1: 90, 2: 70, 3: 55, 4: 40, 5: 30, 6: 20}
    prizeMoneyDict[22] = {1: 90, 2: 70, 3: 55, 4: 40, 5: 30, 6: 20, 7: 15}
    prizeMoneyDict[23] = {1: 95, 2: 75, 3: 60, 4: 40, 5: 30, 6: 20, 7: 15}
    prizeMoneyDict[24] = {1: 95, 2: 75, 3: 60, 4: 40, 5: 30, 6: 20, 7: 20, 8: 10}


    def get_prize_money_dictionary_for_num_players(self, players):
        if players >=24:
            players = 24

        if players < 6:
            return {"Not Enough Players": "Please Come Up With Your Own Game"}

        return self.prizeMoneyDict[players]

    def __str__(self):
        return "Dogfight on {} | {}".format(self.course.name, self.date)

    def formal_text(self):
        return "The Current Dogfight is at {} on {}.<br /> There are {} Tee Times starting at {}. <br /><br />".format(self.course.name, self.date, self.number_of_groups, self.start_time)

    def max_num_of_players(self):
        return self.number_of_groups * 4


# class DogfightPlayer(models.Model):
#     dogfight = models.ForeignKey(Dogfight, related_name='dogfight', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
#     waiting = models.BooleanField(default=False, blank=False, null=False)
#
#     def __str__(self):
#         return "{}, {}".format(self.user.last_name, self.user.first_name)

