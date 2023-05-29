from django.contrib.auth.mixins import LoginRequiredMixin


class ReMixinLoginRequired(LoginRequiredMixin):
    login_url = '/user/login/'
