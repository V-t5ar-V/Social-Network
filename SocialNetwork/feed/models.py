from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from randomslugfield import RandomSlugField
# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='tags', blank=True)
    slug = RandomSlugField(length=10, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Media(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/')

class Tag(models.Model):
    tag = models.SlugField(max_length=20, unique=True, primary_key=True)

class Comment(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post')

class Post_View(models.Model):
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)