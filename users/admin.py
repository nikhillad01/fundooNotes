from django.contrib import admin
from .models import Profile, Notes


# register profile and Note model to admin
admin.site.register(Profile)
admin.site.register(Notes)


class NoteAdmin(admin.ModelAdmin):
    class Meta:
        model = Notes


