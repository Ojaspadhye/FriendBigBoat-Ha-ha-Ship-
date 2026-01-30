from django.urls import path
from friends_user import views

urlpatterns = [
    path("", views.home_views, name="home"),
    path("signup/", views.signup_views, name="signup"),
    path("login/", views.login_views, name="login"),
    path("dashboard/", views.dashboard_views, name="dashboard"),
]