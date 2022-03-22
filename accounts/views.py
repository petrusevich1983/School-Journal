from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from journal.settings import SCHOOLBOY


class UserTypeRedirectView(LoginRequiredMixin, RedirectView):
    """
    Редирект после прохождения авторизации
    """
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.user_status == SCHOOLBOY:
            return reverse_lazy('schoolboy_lk')
        else:
            return reverse_lazy('group_schoolboy_list')
