import requests
from datetime import datetime, timedelta
from sitewide.models import ZappyUser, LastCommit
from money.models import Month
from django.db.models import Avg
from sitewide.git_token import *


class DateTools:
    def __init__(self, date_1, date_2):
        self.date_one, self.date_two = date_1, date_2

    # func return time difference between to dates
    def get_delta(self):
        __delta = self.date_one - self.date_two
        if __delta.days > 0:
            return str(__delta.days) + ' days'
        elif __delta.seconds // 3600 > 0:
            return str(__delta.seconds // 3600) + ' hours'
        elif __delta.seconds // 60 > 0:
            return str(__delta.seconds // 3600) + ' minutes'
        elif __delta.seconds > 0:
            return str(__delta.seconds) + ' seconds'
        else:
            return 'just a moment'


def zappy_footer(request):
    # try in case no objects in database
    try:
        __last_known_commit = LastCommit.objects.first()
        __update_date = __last_known_commit.last_update.replace(tzinfo=None)
        __commit_url = __last_known_commit.commit_url
    except AttributeError:
        __last_known_commit = LastCommit()
        __update_date = datetime.now() - timedelta(days=365)
        __commit_url = 'https://github.com/zappycode/zappycode-django'

    # conditional request - if-modified-since return false,
    # will raise code 304 and not counts against github rate limits
    __commits = requests.get('http://api.github.com/repos/zappycode/zappycode-django/commits',
                           auth=('user', git_token),
                           headers={'Authorization': git_token,
                                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
                                    'If-Modified-Since': __update_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
                                    },
                           )

    if __commits.status_code == 200:
        __last_commit = __commits.json()[0]

        # convert date string to datetime format
        __update_date = datetime.strptime(__last_commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
        __commit_url = __last_commit['html_url']

        # save to db new data
        __last_known_commit.last_update = __update_date
        __last_known_commit.commit_url = __commit_url
        __last_known_commit.save()

    # count time difference from now
    __last_update = DateTools(datetime.utcnow(), __update_date).get_delta()
    __amount_members = ZappyUser.objects.all().count()
    __earnings = Month.objects.all().aggregate(revenue=Avg('revenue') - Avg('expenses'))

    context = {
        "last_commit": __last_update,
        "commit_url": __commit_url,
        "amount_members": __amount_members,
        "earnings": __earnings['revenue'],
    }
    return context
