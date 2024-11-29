from django.contrib.auth import login


def social_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)

    user = social.user if social else None

    return {'social': social, 'user': user, 'is_new': user is None, 'new_association': social is None}


