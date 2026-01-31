from django.urls import path
from friendships import views

urlpatterns = [
    path("friendships/request/", views.sending_friends_request, name="sending_request"),
    path("friendships/request/respond/", views.respond_friend_request, name="responding_request"),
    path("friendships/friends/", views.get_all_friends, name="list_friends"),
    path("friendships/pending/", views.get_all_pending_request, name="pending_requests"),
]
