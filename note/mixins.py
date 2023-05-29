from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.views import View


class ReMixinLoginRequired(LoginRequiredMixin):
    login_url = '/user/login/'


class ReMixinGuardDispatchSingleObject(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            hasattr(self, 'get_object') and self.get_object()
        except Http404 as e:
            return render(self.request, 'note/custom_error.html', context={
                'error_message': 'Bad Request: {}'.format(e)
            }, status=400)

        if hasattr(self, 'test_func') and not self.test_func():
            return render(self.request, 'note/custom_error.html', context={
                'error_message': 'Bad Request: Permission Denied'
            }, status=400)

        return super().dispatch(request, *args, **kwargs)
