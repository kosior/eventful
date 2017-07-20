from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class FriendRequestManager(models.Manager):
    def send_friend_request(self, from_user, to_user_pk):
        if from_user.pk == to_user_pk:
            raise ValidationError('from_user and to_user cannot be identical')

        if from_user.profile.friends.filter(pk=to_user_pk).exists():
            raise ValidationError('already friends')

        if self.filter(from_user_id=to_user_pk, to_user=from_user).exists():
            raise ValidationError('friend request already created')

        _, created = self.get_or_create(from_user=from_user, to_user_id=to_user_pk)

        if created:
            return True
        return False

    def get_request(self, request_user, user_pk):
        users = (request_user.pk, user_pk)
        return self.filter(from_user_id__in=users, to_user_id__in=users)

    def _delete_request(self, from_user, to_user_pk):
        if self.get_request(from_user, to_user_pk).delete():
            return True
        return False

    def accept(self, user_accepting, from_user_pk):
        if self._delete_request(user_accepting, from_user_pk):
            user_accepting.profile.friends.add(from_user_pk)
            return True
        return False

    def reject(self, user_rejecting, from_user_pk):
        return self._delete_request(user_rejecting, from_user_pk)

    def remove_friend(self, request_user, user_pk):
        request_user.profile.friends.remove(user_pk)
        return True

    def get_with_related(self, request_user, user_pk):
        request = self.get_request(request_user, user_pk).select_related('from_user', 'to_user')
        return request.only('from_user__username', 'to_user__username').first()

    def get_all(self, user):
        return self.filter(
            Q(from_user=user) |
            Q(to_user=user)
        ).select_related('from_user', 'to_user').only('from_user__username', 'to_user__username')

    def get_all_grouped(self, user):
        grouped = {'sent': [], 'pending': []}
        for request in list(self.get_all(user)):
            if request.from_user == user:
                grouped['sent'].append(request)
            elif request.to_user == user:
                grouped['pending'].append(request)
        return grouped
