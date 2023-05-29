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


class NoteViewsAuthorizationTestCase(TestCase):
    def setUp(self):
        # Arrange: 2 user and 2 notes each
        self.user_1 = User.objects.create_user(username='test_user_1', password='test_password')
        self.note_1_1 = Note.objects.create(
            title='Test Note 1: user 1', content='This is a test note', author=self.user_1
        )
        self.note_1_2 = Note.objects.create(
            title='Test Note 2: user 1', content='This is a test note', author=self.user_1
        )

        self.user_2 = User.objects.create_user(username='test_user_2', password='test_password')
        self.note_2_1 = Note.objects.create(
            title='Test Note 1: user 2', content='This is a test note', author=self.user_2
        )
        self.note_2_2 = Note.objects.create(
            title='Test Note 2: user 2', content='This is a test note', author=self.user_2
        )

    def _login_and_redirect_to_index(self, username, password):
        # Act: login with user credentials
        url = reverse('noteapp:login')
        response = self.client.post(url, {'username': username, 'password': password})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('noteapp:index'))
        # Redirect
        response = self.client.get(reverse('noteapp:index'))
        # Assert: logged-in username in the page
        self.assertContains(response, "Welcome, {}".format(username))

        return response

    def test_user_1_can_see_only_self_notes_in_index(self):
        response = self._login_and_redirect_to_index('test_user_1', 'test_password')

        self.assertEqual(Note.objects.count(), 4)

        self.assertContains(response, self.note_1_1)
        self.assertContains(response, self.note_1_2)
        self.assertNotContains(response, self.note_2_1)
        self.assertNotContains(response, self.note_2_2)

    def test_user_1_cannot_see_other_notes_single_view(self):
        # Act
        _ = self._login_and_redirect_to_index('test_user_1', 'test_password')

        # Act: visit own note
        url = reverse('noteapp:single', kwargs={'pk': self.note_1_1.pk})
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note/single.html')
        self.assertEqual(response.context['note'], self.note_1_1)

        # Act: visit other's note
        url = reverse('noteapp:single', kwargs={'pk': self.note_2_1.pk})
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.context, None)

    def test_user_1_cannot_edit_other_notes(self):
        # Act
        _ = self._login_and_redirect_to_index('test_user_1', 'test_password')

        # Act: visit own note
        url = reverse('noteapp:edit', kwargs={'pk': self.note_1_1.pk})
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note/edit.html')
        self.assertEqual(response.context['note'], self.note_1_1)

        # Act: visit other's note
        url = reverse('noteapp:edit', kwargs={'pk': self.note_2_1.pk})
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.context, None)

    def test_must_login_for_single_view(self):
        # Act: view note without log in
        url = reverse('noteapp:single', kwargs={'pk': self.note_1_1.pk})
        response = self.client.get(url)
        # Assert: redirect to log in with target url as next
        self.assertEqual(response.status_code, 302)
        next_url = url
        actual_redirect_url = reverse('noteapp:login') + f'?next={next_url}'
        self.assertRedirects(response, actual_redirect_url)

    def test_must_login_for_edit_view(self):
        # Act: edit note without log in
        url = reverse('noteapp:edit', kwargs={'pk': self.note_1_1.pk})
        response = self.client.get(url)
        # Assert: redirect to log in with target url as next
        self.assertEqual(response.status_code, 302)
        next_url = url
        actual_redirect_url = reverse('noteapp:login') + f'?next={next_url}'
        self.assertRedirects(response, actual_redirect_url)
