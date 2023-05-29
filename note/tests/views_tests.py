from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from note.models import Note


class NoteViewsCRUDTestCase(TestCase):
    def setUp(self):
        # Arrange
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')
        self.note = Note.objects.create(title='Test Note', content='This is a test note', author=self.user)

    def test_index_view(self):
        # Act
        response = self.client.get(reverse('noteapp:index'))
        # Assert: correct index view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note/index.html')
        self.assertContains(response, self.note.title)

    def test_single_view(self):
        # Act
        url = reverse('noteapp:single', kwargs={'pk': self.note.pk})
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note/single.html')
        self.assertEqual(response.context['note'], self.note)

    def test_add_view(self):
        # Act
        url = reverse('noteapp:add')
        response = self.client.get(url)
        # Assert: correct add view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note/add.html')
        # Act: post form data
        form_data = {
            'title': 'New Note',
            'content': 'This is a new note',
        }
        response = self.client.post(url, data=form_data)
        # Assert: correct redirection and note creation
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('noteapp:index'))
        self.assertEqual(Note.objects.count(), 2)

    def test_edit_view(self):
        # Act
        url = reverse('noteapp:edit', kwargs={'pk': self.note.pk})
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note/edit.html')
        # Act
        form_data = {
            'title': 'Updated Note',
            'content': 'This note has been updated',
        }
        response = self.client.post(url, data=form_data)
        # Assert: correct redirection and update
        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')
        self.assertEqual(self.note.content, 'This note has been updated')

    def test_delete_view(self):
        # Act
        url = reverse('noteapp:delete', kwargs={'pk': self.note.pk})
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note/delete.html')
        # Act: submit form
        response = self.client.post(url)
        # Assert: redirect to index and successful deletion
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('noteapp:index'))
        self.assertEqual(Note.objects.count(), 0)


class NoteViewsAuthTestCase(TestCase):
    def setUp(self):
        # Arrange
        self.user_original_password = 'test_password'
        self.user = User.objects.create_user(username='test_user', password=self.user_original_password)
        self.note = Note.objects.create(title='Test Note', content='This is a test note', author=self.user)

    def test_original_password_is_not_saved_password(self):
        # Assert
        self.assertNotEqual(self.user_original_password, self.user.password)

    def test_user_login(self):
        # Act: login with user credentials
        url = reverse('noteapp:login')
        response = self.client.post(url, {'username': self.user.username, 'password': self.user_original_password})
        # Assert: correct redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('noteapp:index'))
        # Act: redirect
        response = self.client.get(reverse('noteapp:index'))
        # Assert: logged-in username in the page
        self.assertContains(response, "Welcome, {}".format(self.user.username))

    def test_user_logout(self):
        # Act: login and request logout
        self.client.login(username=self.user.username, password=self.user_original_password)
        url = reverse('noteapp:logout')
        response = self.client.get(url)
        # Assert: correct redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('noteapp:index'))
        # Act: request login page for not logged-in user
        response = self.client.get(reverse('noteapp:index'))
        # Assert: not logged-in user redirected to login page
        self.assertEqual(response.status_code, 302)
        next_url = reverse('noteapp:index')
        actual_redirect_url = reverse('noteapp:login') + f'?next={next_url}'
        self.assertEqual(response.url, actual_redirect_url)
        self.assertRedirects(response, actual_redirect_url)
        # Act: redirect
        response = self.client.get(response.url)
        # Assert: logged-in username not in the page
        self.assertNotContains(response, "Welcome, {}".format(self.user.username))

    def test_user_signup(self):
        # Act: signup new user
        url = reverse('noteapp:signup')
        form_data = {
            'username': 'test_user_2',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        response = self.client.post(url, data=form_data)
        # Assert: redirect to login page on success and new user created
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('noteapp:login'))
        self.assertEqual(User.objects.count(), 2)


class IndexViewSearchTestCase(TestCase):
    def setUp(self):
        # Arrange
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')
        self.note1 = Note.objects.create(title='Test Note1', content='This is a test note', author=self.user)
        self.note2 = Note.objects.create(title='Test Note2', content='This is a test note', author=self.user)
        self.note3 = Note.objects.create(title='Something else', content='Something else', author=self.user)

    def test_search_query(self):
        url = reverse('noteapp:index')
        response = self.client.get(url, {'search': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note1.title)
        self.assertContains(response, self.note2.title)
        self.assertNotContains(response, self.note3.title)
