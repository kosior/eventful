from django.core.cache import cache


def notify_context_processor(request):
    key = f'invites-{request.user.pk}'
    invites_num = cache.get(key)
    if invites_num:
        return {'friend_invites_num': invites_num}
    return {}
