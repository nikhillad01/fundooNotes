from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.widgets import AdminDateWidget
from .models import Profile,Notes
from PIL import Image


# create form for register new user
class UseRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# create form for login
class LoginForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password']


# create form for user update
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


# create form for profile update
class ProfileUpdateForm(forms.ModelForm):
    # Hidden inputs for crop the image
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Profile

        fields = ['image','x', 'y', 'width', 'height',]

    def save(self):
        photo = super(ProfileUpdateForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        # open image
        img = Image.open(photo.image)
        # crop image based on given above co-ordinates x,y,w,h
        cropped_image = img.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        # save cropped image
        resized_image.save(photo.image.path)
        # return cropped image
        return photo


class CreateNoteForm(forms.ModelForm):
    remainder = forms.DateField(widget=AdminDateWidget)

    class Meta:
        model = Notes
        widgets = {
          'description': forms.Textarea(attrs={'rows':1, 'cols':25})
        }
        fields = ('title', 'description', 'is_pinned', 'color','remainder')


class UpdateNoteForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    remainder = forms.DateField(widget=AdminDateWidget)

    class Meta:
        model = Notes
        fields = ['id', 'title', 'description', 'is_pinned', 'color','remainder']


