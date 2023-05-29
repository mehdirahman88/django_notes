Demonstration of various django concepts through a note-taking web application.

# Functionalities
- User should be able to:
  - signup, login and logout (authentication)
  - see only own data (authorization)
  - create note with title and content
  - list all their notes in a page
  - click on a note and check detail of that note
  - edit note
  - delete note
  - search note on title or content


# Django Concepts
- Generic views
- Forms
- Mixin
- Template and bootstrap
- Unit test


# How to run
- create virtual environment if necessary (Python 3.9)
- install requirements
  - `pip install -r requirements.txt`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py runserver`