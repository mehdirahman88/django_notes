from django import forms

from .models import Note


class NoteAddForm(forms.ModelForm):
    title = forms.CharField(label='Title (Max length: 50)', min_length=5, max_length=50)

    class Meta:
        model = Note
        exclude = ['created', 'author']


class NoteEditForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = '__all__'
        exclude = ['author', 'created']



