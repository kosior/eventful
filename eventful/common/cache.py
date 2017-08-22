from django.core.cache import cache


def notify_by_cache(prefix, pk):
    key = f'{prefix}-{pk}'
    if cache.get(key):
        cache.incr(key)
    else:
        cache.set(key, 1)


def decr_notification(prefix, pk):
    key = f'{prefix}-{pk}'
    invites_num = cache.get(key)
    if invites_num:
        cache.decr(key, invites_num)
