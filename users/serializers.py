from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notes


class NoteSerializer(serializers.ModelSerializer):

	class Meta:
		model = Notes
		fields = '__all__'



