import random, string
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='tags', blank=True)
    slug = models.SlugField(max_length=25, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:

            queryset = Post.objects.all()

            while True:
                characters = string.ascii_lowercase + string.digits
                slug = ''.join(random.choice(characters) for _ in range(25))
                if not queryset.filter(slug=slug).exists():
                    break

            self.slug = slugify(slug)
        super().save(*args, **kwargs)



class Media(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='media/')

class Tag(models.Model):
    tag = models.SlugField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        self.tag = slugify(self.tag)
        super().save(*args, **kwargs)

class Comment(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')

class Like(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post')

class Post_View(models.Model):
    viewer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True)