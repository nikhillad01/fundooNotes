from django.contrib import admin
from .models import Profile, Notes ,Labels


# register profile and Note model to admin
admin.site.register(Profile)
admin.site.register(Notes)
admin.site.register(Labels)


class NoteAdmin(admin.ModelAdmin):
    class Meta:
        model = Notes




