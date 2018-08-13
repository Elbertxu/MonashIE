from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Register your models here.
admin.site.register(Profile)
admin.site.register(Quest)
admin.site.register(Event)
admin.site.register(Organizer)
admin.site.register(Evaluation)
admin.site.register(Tag)



class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'user_profile'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
