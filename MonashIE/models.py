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


# Create Organizer Class
class Organizer(models.Model):
    title = models.TextField(max_length=50, default="Not Created")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    description = models.TextField(max_length=500)
    type = models.CharField(max_length=50, blank=True)
    created_date = models.DateTimeField()
    scheduled_time = models.DateTimeField()

    def get_title(self):
        return self.title

    def get_owner(self):
        return self.owner

    def get_description(self):
        return self.description

    def get_type(self):
        return self.type

    def get_created_date(self):
        return self.created_date

    def get_scheduled_time(self):
        return self.scheduled_time

    def set_created_date(self):
        self.created_date = timezone.now()

    def __str__(self):
        return self.title


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
    assistants = [models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, )]
    accept_status = models.TextField(max_length=20, default="Not Accepted")
    accept_date = models.DateTimeField(blank=True, null=True)
    document = models.FileField(upload_to='documents/', null=True, validators=[validate_file_extension])
    document_upload_date = models.DateTimeField(auto_now_add=True)
    organizer = models.ForeignKey(Organizer, null=True, on_delete=models.PROTECT)
    tags = models.ManyToManyField('Tag')

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_type(self):
        return self.type

    def get_intro(self):
        return self.intro

    def get_review_status(self):
        return self.review_status

    def get_accept_status(self):
        return self.accept_status

    def get_assistants(self):
        return self.assistants

    def get_submission_date(self):
        return self.submission_date

    def get_document(self):
        if not self.document:
            return "Not Submitted"
        else:
            return self.document.name.replace("documents/", "")

    def get_organization(self):
        return self.organizer

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


# Create Comments Class
class Evaluation(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', null=True, on_delete=models.PROTECT)
    evaluation = models.FileField(upload_to='evaluations/', null=True, validators=[validate_file_extension])
    upload_date = models.DateTimeField(auto_now_add=True, null=True)

    def get_evaluation_name(self):
        if not self.evaluation:
            return "Not Submitted"
        else:
            return self.evaluation.name.replace("evaluations/", "")

    def __str__(self):
        return self.evaluation.name.replace("evaluations/", "")


# Create Event Class
class Event(models.Model):
    organizer = models.ForeignKey('Organizer', null=True, on_delete=models.PROTECT)
    title = models.CharField(max_length=50, default="Not Created")
    quest_to_review = models.ForeignKey('Quest', null=True, on_delete=models.PROTECT)
    assistant_list = models.CharField(max_length=100, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    scheduled_time = models.DateTimeField(null=True)

    def get_organization(self):
        return self.organizer

    def get_title(self):
        return self.title

#    def get_description(self):
#        return self.description

    def get_created_date(self):
        return self.created_date

    def get_scheduled_time(self):
        return self.scheduled_time

    def get_quest_to_review(self):
        return self.quest_to_review

    def get_assistant_list(self):
        return self.assistant_list

    def set_created_date(self):
        self.created_date = timezone.now()

    def __str__(self):
        return self.title


