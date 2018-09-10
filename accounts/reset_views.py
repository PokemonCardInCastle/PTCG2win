from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class AccountsPasswordResetView(auth_views.PasswordResetView):
    success_url = reverse_lazy('accounts:password_reset_done')

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    success_url = reverse_lazy('accounts:password_reset_done')

