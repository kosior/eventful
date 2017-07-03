from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from invitations.models import FriendInvitation


@method_decorator(login_required, name='dispatch')
class SendFriendRequest(View):
    http_method_names = [u'post']

    def post(self, request):
        to_user = get_object_or_404(User, pk=request.POST.get('to_user'))
        try:
            FriendInvitation.objects.create(inviter=request.user, to_user=to_user)
        except IntegrityError:
            return JsonResponse({'created': False})
        else:
            return JsonResponse({'created': True})
