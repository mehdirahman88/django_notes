from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import NoteAddForm, NoteEditForm
from .models import Note


# Create your views here.
class IndexView(ListView):
    model = Note
    template_name = 'note/index.html'
    context_object_name = 'note_list'


class SingleView(DetailView):
    model = Note
    template_name = 'note/single.html'
    context_object_name = 'note'


class AddView(CreateView):
    model = Note
    form_class = NoteAddForm
    template_name = 'note/add.html'
    success_url = reverse_lazy('noteapp:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class EditView(UpdateView):
    model = Note
    form_class = NoteEditForm
    template_name = 'note/edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('noteapp:index')


class Delete(DeleteView):
    model = Note
    template_name = 'note/delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('noteapp:index')

