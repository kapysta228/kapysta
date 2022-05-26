from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import UpdateView, CreateView

from .forms import LoginForm, UserForm, SignupForm, CustomPasswordChangeForm


# Create your views here.
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        if not self.request.GET:
            self.extra_context = {'next': '/'}
        return super().get(request, *args, **kwargs)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('a-login')
    form_class = UserForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('a-profile-update')

    def get_object(self, queryset=None):
        return self.request.user


class SignupView(CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('a-profile-update')
    template_name = 'accounts/signup.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            login(self.request, auth_user)
        return form_valid


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    login_url = reverse_lazy('a-login')
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('a-profile-update')  # Переадресация при успешной смене
    form_class = CustomPasswordChangeForm
