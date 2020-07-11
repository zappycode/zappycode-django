from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from invites.models import Invite
from django.template.defaultfilters import pluralize
from django.contrib.auth.decorators import login_required
import allauth.account.views


def invite_landing_page(request, token):
    if request.method == 'POST':
        return InviteSignupView.as_view()(request)
    else:
        invite = get_object_or_404(Invite, token=token)
        return render(request, 'invites/invite_landing_page.html', {'invite': invite})


class InviteSignupView(allauth.account.views.SignupView):
    template_name = 'invites/invite_landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invite'] = get_object_or_404(Invite, token=self.request.POST.get("invite", ""))
        return context


@login_required
def redeem_invite_to_existing_account(request, token):
    invite = get_object_or_404(Invite, token=token)

    if not invite.is_expired():
        if invite.receiver is None:
            if not request.user.active_membership:
                invite.receiver = request.user
                invite.save()
                request.user.active_membership = True
                request.user.save()
                messages.success(request,
                                 f'You now have free access to ZappyCode for the next {invite.days_left()} day{pluralize(invite.days_left())}!')
    else:
        messages.success(request,
                         f'Unable to redeem the invite 😩')

    return redirect('home')
