from django.urls import path
from .views import csrf_view, login_view, logout_view, me_view, signup,  verify_email

urlpatterns = [
    path("csrf/", csrf_view, name="csrf"),
    path("login/", login_view, name="login"),
    path('signup/', signup, name='signup'),
    path("verify/", verify_email),
    path("logout/", logout_view, name="logout"),
    path("me/", me_view, name="me"),
]