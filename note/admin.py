from django.contrib import admin

from note.models import Note


# Register your models here.
@admin.register(Note)
class PostAdmin(admin.ModelAdmin):
    pass
