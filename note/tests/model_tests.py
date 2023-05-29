from django.contrib.auth.models import User
from django.test import TestCase

from note.models import Note


class NoteModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.note = Note.objects.create(title='Test Note', content='This is a test note', author=self.user)

    def test_model_representation(self):
        # Act
        first_note_obj = Note.objects.first()
        # Assert
        self.assertEqual(str(first_note_obj), first_note_obj.title)

    def test_create_note_without_user(self):
        # Assert: non-existent user cannot create note
        with self.assertRaises(ValueError):
            Note.objects.create(
                title='Test Note',
                content='This is a test note',
                author="non_existent_user",
            )

