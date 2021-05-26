import requests
from datetime import datetime, timedelta
from sitewide.models import ZappyUser, LastCommit
from money.models import Month
from django.db.models import Avg
from django.template.defaultfilters import pluralize
from django.utils import timezone
import environ

env = environ.Env()
environ.Env.read_env()


class DateTools:
    def __init__(self, date_1, date_2):
        self.date_one, self.date_two = date_1, date_2

    # func return time difference between to dates
    def get_delta(self):
        delta = self.date_one - self.date_two
        if delta.days > 0:
            return str(delta.days) + f' day{pluralize(delta.days)}'
        elif delta.seconds // 3600 > 0:
            return str(delta.seconds // 3600) + f' hour{pluralize(delta.seconds // 3600)}'
        elif delta.seconds // 60 > 0:
            return str(delta.seconds // 60) + f' minute{pluralize(delta.seconds // 60)}'
        elif delta.seconds > 0:
            return str(delta.seconds) + f' second{pluralize(delta.seconds)}'
        else:
            return 'just a moment'


def zappy_footer(request):
    # try in case no objects in database
    try:
        last_known_commit = LastCommit.objects.first()
    except:
        last_known_commit = LastCommit()
        last_known_commit.commit_time = timezone.now()
        last_known_commit.last_checked = timezone.now()
        last_known_commit.commit_url = 'https://github.com/zappycode/zappycode-django'
        last_known_commit.save()

    timediff = timezone.now() - last_known_commit.last_checked

    if timediff.seconds > 300:

        last_known_commit.last_checked = timezone.now()
        last_known_commit.save()

        commits = requests.get('http://api.github.com/repos/zappycode/zappycode-django/commits',
                               auth=('user', env.str('GITHUB_API_KEY', default='')),
                               headers={'Authorization': env.str('GITHUB_API_KEY', default=''), },
                               )

        if commits.status_code == 200:
            last_commit = commits.json()[0]

            # convert date string to datetime format
            last_known_commit.commit_time = datetime.strptime(last_commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
            last_known_commit.commit_url = last_commit['html_url']

            # save to db new data
            last_known_commit.save()

    # count time difference from now
    last_update = DateTools(timezone.now(), last_known_commit.commit_time).get_delta()
    amount_members = ZappyUser.objects.all().filter(active_membership=True).count()
    latest_month = Month.objects.order_by('-year', '-month').first()

    context = {
        "last_commit": last_update,
        "commit_url": last_known_commit.commit_url,
        "amount_members": amount_members,
        "latest_month": latest_month,
    }
    return context
