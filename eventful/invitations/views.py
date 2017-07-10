from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView

from .models import FriendInvitation


@method_decorator(login_required, name='dispatch')
class InvitationsList(ListView):
    context_object_name = 'friend_invitations'
    template_name = 'invitations/invitations.html'

    def get_queryset(self):
        return FriendInvitation.objects.get_user_pending_invitations(self.request.user)


class FriendRequestMixin:
    http_method_names = [u'post']

    def post(self, request):
        kwargs = {'from_user_pk': request.user.pk, 'to_user_pk': int(request.POST.get('pk'))}
        result = self.manager_method(**kwargs)
        return JsonResponse({'result': result})


@method_decorator(login_required, name='dispatch')
class SendFriendRequest(FriendRequestMixin, View):
    manager_method = FriendInvitation.objects.send_invitation


@method_decorator(login_required, name='dispatch')
class AcceptFriendRequest(FriendRequestMixin, View):
    manager_method = FriendInvitation.objects.accept


@method_decorator(login_required, name='dispatch')
class RejectFriendRequest(FriendRequestMixin, View):
    manager_method = FriendInvitation.objects.reject


@method_decorator(login_required, name='dispatch')
class ShowFriends(ListView):
    context_object_name = 'friend_invitations'
    template_name = 'invitations/friends.html'

    def get_queryset(self):
        return FriendInvitation.objects.get_friends(self.request.user)
