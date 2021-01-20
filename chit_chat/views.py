from datetime import datetime
import requests
import base64
import hmac
import hashlib
from urllib import parse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect

from zappycode.settings import DISCOURSE_BASE_URL, DISCOURSE_API_KEY, DISCOURSE_USER_NAME


def get_category(headers, category_id):
    response = requests.get(DISCOURSE_BASE_URL + '/c/' + str(category_id) + '/show.json', headers)
    if response.status_code == 200:
        category = response.json()['category']
    else:
        category = None
    return category


# function to get discourse topics for lectures or courses. using discourse APi
def get_topics(course_slug=''):
    headers = {'Api-Username': DISCOURSE_USER_NAME,
               'Api-Key': DISCOURSE_API_KEY,
               'Accept': 'application/json'}
    number_of_topics = 10
    table_title = 'Recent Chit Chat Issues'
    category_details = None

    if 'django'.capitalize() in course_slug.capitalize() or 'python'.capitalize() in course_slug.capitalize():
        response = requests.get(DISCOURSE_BASE_URL + '/c/6.json', headers)
        table_title = 'Recent Django Issues'
    elif 'kotlin'.capitalize() in course_slug.capitalize():
        response = requests.get(DISCOURSE_BASE_URL + '/c/7.json', headers)
        table_title = 'Recent Kotlin Issues'
    elif 'swift'.capitalize() in course_slug.capitalize() or 'swiftui'.capitalize() in course_slug.capitalize() or 'ios'.capitalize() in course_slug.capitalize():
        response = requests.get(DISCOURSE_BASE_URL + '/c/8.json', headers)
        table_title = 'Recent Swift Issues'
    elif course_slug == 'last':
        response = requests.get(DISCOURSE_BASE_URL + '/latest.json', headers)
        number_of_topics = 4
    else:
        response = requests.get(DISCOURSE_BASE_URL + '/top/quarterly.json', headers)
        table_title = 'Most Popular Issues'
        course_slug = 'top'
        number_of_topics = 5

    if response.status_code == 200:
        topics_list = response.json()['topic_list']['topics'][:number_of_topics]
        topics = []
        i = 1
        for topic in topics_list:
            posters = {
                'Orig': None,
                'Most': None,
            }
            if course_slug == 'last' or course_slug == 'top':
                category_details = get_category(headers, topic['category_id'])
            for poster in topic['posters']:
                description = poster['description']
                if 'Original Poster' in description or 'Most Recent Poster' in description:
                    key = poster['description'][:4]
                    users = next(user for user in response.json()['users'] if user['id'] == poster['user_id'])
                    users['avatar_template'] = '/user_avatar/' + DISCOURSE_BASE_URL[(DISCOURSE_BASE_URL.find('://') + 3):] + '/' + users['username'] \
                                               + '/25' + users['avatar_template'][users['avatar_template'].rfind('/'):]
                    posters[key] = {'poster': users, 'description': description}

            if topic['last_posted_at']:
                last_posted_at = topic['last_posted_at']
            else:
                last_posted_at =  topic['created_at']

            context = {
                'id': topic['id'],
                'title': topic['title'],
                'slug': topic['slug'],
                'category': category_details,
                'tags': topic['tags'],
                'posters': posters,
                'posts_count': topic['posts_count'] - 1,
                'views': topic['views'],
                'created_at': datetime.strptime(topic['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                'last_posted_at': datetime.strptime(last_posted_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            }
            topics.append(context)
    else:
        topics = None
        table_title = None
    return topics, table_title


@login_required
def discourse_sso(request):
    """
    Django view function registered with `urls.py` and used as the callback
    in Discourse configuration.

    Make sure to set `DISCOURSE_BASE_URL` and `DISCOURSE_SSO_SECRET` in settings.py

    Code from https://gist.github.com/alee/3c6161809ef78966454e434a8ed350d1
    """
    payload = request.GET.get('sso')
    signature = request.GET.get('sig')

    if None in [payload, signature]:
        return HttpResponseBadRequest('No SSO payload or signature. Please contact support if this problem persists.')

    # Validate the payload
    payload = bytes(parse.unquote(payload), encoding='utf-8')
    decoded = base64.decodebytes(payload).decode('utf-8')
    if len(payload) == 0 or 'nonce' not in decoded:
        return HttpResponseBadRequest('Invalid payload. Please contact support if this problem persists.')

    key = bytes(settings.DISCOURSE_SSO_SECRET, encoding='utf-8')  # must not be unicode
    h = hmac.new(key, payload, digestmod=hashlib.sha256)
    this_signature = h.hexdigest()

    if not hmac.compare_digest(this_signature, signature):
        return HttpResponseBadRequest('Invalid payload. Please contact support if this problem persists.')

    # Build the return payload
    qs = parse.parse_qs(decoded)
    user = request.user
    params = {
        'nonce': qs['nonce'][0],
        'email': user.email,
        'external_id': user.id,
        'username': user.username,
        # 'require_activation': 'true', we don't need that
        'name': user.get_full_name(),
    }

    return_payload = base64.encodebytes(bytes(parse.urlencode(params), 'utf-8'))
    h = hmac.new(key, return_payload, digestmod=hashlib.sha256)
    query_string = parse.urlencode({'sso': return_payload, 'sig': h.hexdigest()})

    # Redirect back to Discourse
    discourse_sso_url = f'{settings.DISCOURSE_BASE_URL}/session/sso_login?{query_string}'
    return redirect(discourse_sso_url)
