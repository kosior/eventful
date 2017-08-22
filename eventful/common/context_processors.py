from django.core.cache import cache


def notify_context_processor(request):
    context = {}
    pk = request.user.pk
    friend_invites_count = cache.get(f'f_invites_count-{pk}')
    event_invites_count = cache.get(f'e_invites_count-{pk}')
    if friend_invites_count:
        context['friend_invites_count'] = friend_invites_count
    if event_invites_count:
        context['event_invites_count'] = event_invites_count
    return context
