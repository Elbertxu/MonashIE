from django import template
from django.contrib.auth.models import User
from MonashIE.models import Profile
register = template.Library()


@register.inclusion_tag('my_tags.html', takes_context=True)
def my_tags(context):
    request = context.get('request')

    if request.user.username == 'admin':
        links = [
            ['Manage Site', '/admin'],
            ['EVENTS', '/events'],
            ['QUESTS', '/quests'],
            ['Logout', '/logout'],
            ]
        return {'links': links, 'request_user': request.user}

    if request.user.groups.filter(name='Organizer').exists():
        links = [
            ['Home', '/papers'],
            ['Manage Conferences', '/organizers'],
            ['All QUESTS', '/quests'],
            ['Logout', '/logout'],
            ]
        return {'links': links, 'request_user': request.user, 'user_type': ' |Organizer', 'user_field': ''}

    if request.user.groups.filter(name='User').exists():
        links = [
            ['Home', '/quests'],
            ['My Quests', '/quests'],
            ['Submit Quest', '/quest/new'],
            ['Logout', '/logout'],
            ]
        return {'links': links, 'request_user': request.user, 'user_type': ' |User', 'user_field': '|' + request.user.profile.type}

    if request.user.groups.filter(name='Assistant').exists():
        links = [
            ['Home', '/quests'],
            ['My Events', '/events'],
            ['Logout', '/logout'],
        ]
        return {'links': links, 'request_user': request.user, 'user_type': '| Assistant', 'user_field': '|' + request.user.profile.type}

    else:
        links = [
            ['Home', '/quests'],
            ['Quests', '/quests'],
            ['My Events', '/events'],
            ['Logout', '/logout'],
            ]
        return {'links': links, 'request_user': 'Guest', 'user_type': '', 'user_field': ''}
