from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import UserLoginView, UserUpdateView, SignupView, CustomPasswordChangeView

urlpatterns = [
    path('profile/', UserUpdateView.as_view(), name='a-profile-update'),
    path('login/', UserLoginView.as_view(), name='a-login'),
    path('signup/', SignupView.as_view(), name='a-signup'),
    path('logout/', LogoutView.as_view(next_page='/'), name='a-logout'),
    path('change-password', CustomPasswordChangeView.as_view(), name='a-change-password')
]
