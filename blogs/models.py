from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy,reverse
from django.utils import timezone
from django.db.models.signals import post_save
from taggit.managers import TaggableManager
from django.utils.text import slugify


# from smartfields import fields
from django_countries.fields import CountryField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=20)
    slug=models.SlugField(null=True, unique=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title
    class Meta:
        ordering=('title',)

class Posts(models.Model):
    title=models.CharField(max_length=255)
    # overview = models.TextField()
    slug = models.SlugField(null=True, unique=True) 
    user = models.ForeignKey(User, default = 1, on_delete=models.CASCADE)
    content=RichTextUploadingField()
    thumbnail=models.ImageField(upload_to='blogs_images/', blank=True)
    publish=models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True)
    # categories = models.ManyToManyField(Category)
    categories = models.ForeignKey(Category,default = 1, on_delete=models.CASCADE)
    read = models.IntegerField(default = 0)
    tags = TaggableManager()
    likes = models.ManyToManyField(User,related_name='likes',blank= True)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('blog-detail',  args=[str(self.id)])
    class Meta:
    	ordering=('-publish',)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Posts, self).save(*args, **kwargs)



class UserProfile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio=models.CharField(max_length=250,blank=True,null=True)
    birthday=models.DateField(blank=True,null=True) 
    profilepic = models.ImageField(upload_to='users/', blank=True, null=True)
    hobby = models.CharField(max_length=40, blank=True, null=True)
    location = models.CharField(max_length=40, blank=True, null=True)
    country = CountryField(blank=True, null=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Comment(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    comm = models.TextField()

class SubComment(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    comm = models.TextField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
