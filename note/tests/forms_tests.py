from django.contrib.auth.models import User
from django.test import TestCase

from note.forms import NoteAddForm, NoteEditForm
from note.models import Note


class NoteFormsTestCase(TestCase):
    def setUp(self):
        # Arrange
        self.user = User.objects.create_user(username='test_user', password='test_pass')
        self.note_data = {
            'title': 'Test Note',
            'content': 'Test content',
        }

    def test_note_add_form_valid(self):
        # Act
        form = NoteAddForm(data=self.note_data)
        # Assert
        self.assertTrue(form.is_valid())

    def test_note_add_form_invalid(self):
        # Act
        form_data = self.note_data.copy()
        form_data['title'] = ''
        form = NoteAddForm(data=form_data)
        # Assert
        self.assertFalse(form.is_valid())

    def test_note_add_form_save(self):
        # Act
        form = NoteAddForm(data=self.note_data)
        # Assert
        self.assertTrue(form.is_valid())
        # Act
        note = form.save(commit=False)
        note.author = self.user
        note.save()
        # Assert: the note is saved correctly
        self.assertEqual(Note.objects.count(), 1)
        saved_note = Note.objects.first()
        self.assertEqual(saved_note.title, self.note_data['title'])
        self.assertEqual(saved_note.content, self.note_data['content'])
        self.assertEqual(saved_note.author, self.user)

    def test_note_edit_form_valid(self):
        # Act
        note = Note.objects.create(title='Initial Title', content='Initial content', author=self.user)
        form_data = {
            'title': 'Updated Title',
            'content': 'Updated content',
        }
        form = NoteEditForm(data=form_data, instance=note)
        # Assert
        self.assertTrue(form.is_valid())

    def test_note_edit_form_invalid(self):
        # Act
        note = Note.objects.create(title='Initial Title', content='Initial content', author=self.user)
        form_data = {
            'title': '',  # Empty title
            'content': 'Updated content',
        }
        form = NoteEditForm(data=form_data, instance=note)
        # Assert
        self.assertFalse(form.is_valid())

    def test_note_edit_form_save(self):
        # Act
        note = Note.objects.create(title='Initial Title', content='Initial content', author=self.user)
        form_data = {
            'title': 'Updated Title',
            'content': 'Updated content',
        }
        form = NoteEditForm(data=form_data, instance=note)
        # Assert
        self.assertTrue(form.is_valid())
        # Act
        updated_note = form.save()
        # Assert: note is updated correctly
        self.assertEqual(updated_note.title, form_data['title'])
        self.assertEqual(updated_note.content, form_data['content'])


