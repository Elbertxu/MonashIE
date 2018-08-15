from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from .forms import QuestForm, SignUpForm
from .models import Quest, Event, Tag
from .tokens import account_activation_token


@require_http_methods(['GET'])
def search(request):
    q = request.GET.get('q')
    if q:
        quests = Quest.objects.filter(title__contains=q).order_by('submission_date')
        return render(request, 'quest_review.html', {'quests': quests, 'query': q})

    else:
        return HttpResponse('Please submit a search term')


def landing(request):
    return render(request, 'landing.html')


def admin(request):
    return redirect(request, 'admin')


def quest_new(request):
    if request.method == "POST":
        form = QuestForm(request.POST, request.FILES)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.author = request.user
            quest.type = form.cleaned_data.get('type')
            quest.submission_date = timezone.now()
            quest.save()
            return redirect('quest_organizer', pk=quest.pk)
    else:
        form = QuestForm()
    return render(request, 'quest_edit.html', {'form': form})


def quest_edit(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    if request.method == "POST":
        form = QuestForm(request.POST, request.FILES, instance=quest)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.author = request.user
            quest.field = request.user.profile.type
            quest.submission_date = timezone.now()
            quest.save()
            return redirect('quest_organizer', pk=quest.pk)
    else:
        form = QuestForm(instance=quest)
    return render(request, 'quest_edit.html', {'quest': quest, 'form': form})


def quest_list(request):
    if request.user.groups.filter(name='Sponsor').exists():
        quests = Quest.objects.all().order_by('submission_date')
        return render(request, 'quest_review.html', {'quests': quests})

    else:
        quests = Quest.objects.filter(author=request.user).order_by('submission_date')
        return render(request, 'quest_list.html', {'quests': quests})


def quest_detail(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    event = Event.objects.filter(quest_to_review=quest)
    if quest.author == request.user:
        return render(request, 'quest_detail.html', {'quest': quest})
    else:
        return render(request, 'quest_detail_review.html', {'quest': quest})


def create_event(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    assistants_all = []
    assistants_all[:] = []
    users = User.objects.all()
    for user in users:
        if user.profile.field == quest.field and user.groups.filter(name='Assistant').exists():
            user_info = user.username
            assistants_all.insert(0, user_info)

    class EventForm(forms.ModelForm):
        options = []
        options[:] = []
        for user in assistants_all:
            options.insert(0, (user, user))

        assistant_list = forms.MultipleChoiceField(label='Select Assistants in ' + quest.field,
                                                  widget=forms.CheckboxSelectMultiple, choices=options)

        class Meta:
            model = Event
            fields = ('assistant_list',)
            widgets = {
                'datetime': DateTimeWidget(attrs={'id': "yourdatetimeid"}, usel10n=True, bootstrap_version=2)
            }

    if Event.objects.filter(quest_to_review=quest).exists():
        event = Event.objects.filter(quest_to_review=quest)
        event = event[0]
        if request.method == "POST":
            form = EventForm(request.POST, instance=event)          # overwrite the previous event
            if form.is_valid():
                event = form.save()
                event.created_date = timezone.now()
                event.quest_to_review = quest
                event.title = 'Review ' + quest.title
                event.save()
                event.assistant_list = format_str(event.assistant_list)
                event.save()
                assistants = event.assistant_list.split(", ")

                for assistant in assistants:
                    user = User.objects.get(username=assistant)
                    current_site = get_current_site(request)
                    subject = "Sponsor invitation to " + assistant
                    message = render_to_string('notification.html', {
                                'user': user,
                                'paper': quest.title,
                                'date': event.scheduled_time,
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(event.pk)),
                                'token': urlsafe_base64_encode(event.title),
                            })
                    user.email_user(subject, message)
                return redirect('organizer_list')
        else:
            form = EventForm()

    elif request.method == "POST" and not Event.objects.filter(quest_to_review=quest).exists():
            form = EventForm(request.POST)                            # create a new event
            if form.is_valid():
                event = form.save()
                event.created_date = timezone.now()
                event.quest_to_review = quest
                event.title = '<Assist>' + ' ' + quest.title
                event.save()
                event.assistant_list = format_str(event.assistant_list)

                event.save()
                assistants = event.assistant_list.split(", ")
                for assistant in assistants:
                    user = User.objects.get(username=assistant)
                    current_site = get_current_site(request)
                    subject = "Sponsor invitation to " + assistant
                    message = render_to_string('notification.html', {
                                'user': user,
                                'quest': quest.title,
                                'date': event.scheduled_time,
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(quest.pk)),
                                'token': urlsafe_base64_encode(quest.title),
                            })
                    user.email_user(subject, message)
                return redirect('organizer_list')

    else:
        form = EventForm()                                            # form is invalid, re-post
    return render(request, 'create_event.html', {'form': form, 'quest': quest})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    # evaluation_list = []

    return render(request, 'event_detail.html', {'event': event})


def set_reviewed(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    quest.review_status = "Reviewed"
    quest.save()
    return render(request, 'quest_detail_review.html', {'quest': quest})


def set_accepted(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    quest.accept_status = "Accepted"
    quest.save()
    return render(request, 'quest_detail_review.html', {'quest': quest})


# define a global attribute applied_group coz both signup and activate views needs it
applied_group = 'User'


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.refresh_from_db()
            user.profile.field = form.cleaned_data.get('type')
            user.profile.username = form.cleaned_data.get('username')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            global applied_group
            applied_group = form.cleaned_data.get('groups')
            user.save()

            user = authenticate(username=username, password=raw_password)
            # login(request, user)
            user = get_object_or_404(User, username=username)
            current_site = get_current_site(request)
            subject = 'Account Activation'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            message_to_admin = render_to_string('account_activation_email_admin.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
                'applicant_email': email,
            })
            if applied_group == 'Sponsor':
                send_mail(subject, message_to_admin, 'admin@cms.com', ['admin@cms.com']),
                user.email_user(subject, 'Your Application is sent to site administrator for approval! - Monash CMS')
                return render(request, 'account_activation_sent.html', {'email': email})
            else:
                user.email_user(subject, message)
                return render(request, 'account_activation_sent.html', {'email': email})
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        group = Group.objects.get(name=applied_group)
        group.user_set.add(user)
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return redirect('activated')
    else:
        return render(request, 'account_activation_invalid.html')


def notification(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        event = Event.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        event = None
    if urlsafe_base64_decode(token) == event.title:
        return render(request, 'event_detail.html', {'event': event})


def activated(request):
    return render(request, 'account_activated.html')


def format_str(old_str):
    str1 = old_str.replace("u'", "")
    str2 = str1.replace("'", "")
    str3 = str2.replace("[", "")
    new_str = str3.replace("]", "")
    return new_str


def document_download(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    domain = get_current_site()
    return domain/quest.get_document_name()


class TagView(ListView):
    model = Quest
    template_name = 'quest_review.html'
    context_object_name = 'quests'

    def get_queryset(self):
        papers = Quest.objects.filter(tags=self.kwargs['pk'])
        return papers

    def get_context_data(self, **kwargs):
        kwargs['tag_list'] = Tag.objects.all().order_by('name')
        return super(TagView, self).get_context_data(**kwargs)
