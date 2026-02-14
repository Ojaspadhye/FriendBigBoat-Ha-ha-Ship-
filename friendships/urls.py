from django.urls import path
from friendships import views

urlpatterns = [
    path("request/", views.sending_friends_request, name="sending_request"),
    path("request/respond/", views.respond_friend_request, name="responding_request"),
    path("friends/", views.get_all_friends_accepted, name="list_friends"),
    path("request/pending/", views.get_all_pending_request_to_me, name="pending_requests"),
    path("request/sent/pending/", views.get_all_friend_waiting, name="pending_requests_by_me"),
    path("message/send/", views.send_message, name="sending_message")
]
