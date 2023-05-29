from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

from .forms import NoteAddForm, NoteEditForm
from .mixins import ReMixinLoginRequired
from .models import Note


# Create your views here.
class IndexView(ReMixinLoginRequired, ListView):
    model = Note
    template_name = 'note/index.html'
    context_object_name = 'note_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(author=self.request.user)

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset


class SingleView(ReMixinLoginRequired, DetailView):
    model = Note
    template_name = 'note/single.html'
    context_object_name = 'note'


class AddView(ReMixinLoginRequired, CreateView):
    model = Note
    form_class = NoteAddForm
    template_name = 'note/add.html'
    success_url = reverse_lazy('noteapp:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class EditView(ReMixinLoginRequired, UpdateView):
    model = Note
    form_class = NoteEditForm
    template_name = 'note/edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('noteapp:index')


class Delete(ReMixinLoginRequired, UserPassesTestMixin, DeleteView):
    model = Note
    template_name = 'note/delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('noteapp:index')

    def test_func(self):
        item = self.get_object()
        return item.author == self.request.user


class UserLogin(LoginView):
    template_name = 'note/login.html'
    success_url = reverse_lazy('noteapp:index')

    def dispatch(self, request, *args, **kwargs):
        logout(request)  # Logout the user before
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url


class UserLogout(ReMixinLoginRequired, LogoutView):
    template_name = 'note/index.html'
    success_url = reverse_lazy('noteapp:index')

    def get_success_url(self):
        return self.success_url


class UserSignup(FormView):
    template_name = 'note/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('noteapp:login')

    def dispatch(self, request, *args, **kwargs):
        logout(request)  # Logout the user before
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


