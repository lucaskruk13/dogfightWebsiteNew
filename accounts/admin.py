from django.contrib import admin
from accounts.models import Profile, Scores
from feed.models import Dogfight, Course
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class ScoreInline(admin.TabularInline):
    model = Scores
    can_delete = True
    verbose_name_plural = 'Scores'
    fk_name = 'user'

    extra = 1

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, ScoreInline)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)