from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .validators import validate_file_extension
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create a Profile model for users
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30, blank=True)
    USERNAME_FIELD = 'username'
    type = models.CharField(max_length=50, blank=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


# Create Quest Class
class Quest(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(max_length=50, null=False)
    type = models.TextField(max_length=50, null=False)
    intro = models.TextField(max_length=5000, null=True)
    abstract = models.TextField(max_length=5000, null=True)
    submission_date = models.DateTimeField(default=timezone.now, null=True)
    review_status = models.TextField(max_length=20, default="Not Reviewed")
    review_date = models.DateTimeField(blank=True, null=True)
    accept_status = models.TextField(max_length=20, default="Not Accepted")
    accept_date = models.DateTimeField(blank=True, null=True)
    document = models.FileField(upload_to='documents/', null=True)
    document_upload_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag')

    def get_document(self):
        if not self.document:
            return "Not Submitted"
        else:
            return self.document.name.replace("documents/", "")

    def set_submission_date(self):
        self.submission_date = timezone.now()
        self.save()

    def set_review_status(self):
        self.review_status = "Reviewed"
        self.save()

    def set_review_date(self):
        self.review_date = timezone.now()
        self.save()

    def set_accept_status(self):
        self.accept_status = "YES"
        self.save()

    def set_accept_date(self):
        self.accept_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField('Tag', max_length=50)
    created_time = models.DateField('Tag', auto_now_add=True)
    last_modified_time = models.DateField('Tag', auto_now=True)

    def __str__(self):
        return self.name


# Create Event Class
class Event(models.Model):
    sponsor = models.TextField(max_length=50, null=True, default="None")
    title = models.CharField(max_length=50, default="Not Created")
    quest = models.ForeignKey('Quest', null=False, on_delete=models.PROTECT,default=0)
    assistant = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=0)
    created_date = models.DateTimeField(default=timezone.now)
    scheduled_time = models.DateTimeField(null=True)



    def set_created_date(self):
        self.created_date = timezone.now()

    def __str__(self):
        return self.title


