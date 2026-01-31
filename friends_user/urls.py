from django.urls import path
from friends_user import views

urlpatterns = [
    path("", views.home_views, name="home"),
    path("signup/", views.signup_views, name="signup"),
    path("login/", views.login_views, name="login"),
    path("dashboard/", views.dashboard_views, name="dashboard"),
    path("profile/", views.profile_views, name="profile"),
    path("profile/delete/", views.delete_user_views, name="delete_user"),
    path("profile/update/", views.update_profile_views, name="profile_update"),
    path("search/users/", views.list_users_views, name="search_users")
]