from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# create profile model
class Profile(models.Model):

    user=models.OneToOneField(User, on_delete=models.CASCADE)
    # create image field
    image=models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    # def save(self):
    #     super().save()

# create Note model
class Notes(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True,null=True)
    remainder = models.DateTimeField(default=None,null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    color = models.CharField(default=None, max_length=50, blank=True, null=True)
    image = models.ImageField(default=None,null=True)
    trash = models.BooleanField(default=False)
    is_pinned = models.NullBooleanField(blank=True, null=True, default=None)
    label = models.CharField(max_length=50)
    collaborate = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                    related_name='collaborated_user')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('home')













