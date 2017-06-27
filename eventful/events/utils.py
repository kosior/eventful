def is_user_an_author(request, event):
    return request.user == event.created_by
