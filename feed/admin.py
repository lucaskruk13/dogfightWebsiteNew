from django.contrib import admin
from .models import Course, Dogfight
from accounts.models import Scores

class ScoresTabular(admin.TabularInline):
    model = Scores
    extra = 1




class DogfightAdmin(admin.ModelAdmin):
    inlines = [ScoresTabular]




admin.site.register(Course)
admin.site.register(Dogfight, DogfightAdmin)

