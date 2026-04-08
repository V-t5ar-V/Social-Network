from django.db import models
# Create your models here.
class Post(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='tags', null=True, blank=True)

class Media(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/')

class Tag(models.Model):
    tag = models.CharField(max_length=20, primary_key=True)

class Comment(models.Model):
    text = models.CharField(max_length=200)
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

class Like(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('profile', 'post')

class PostView(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    viewer = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)