from __future__ import unicode_literals
from django.utils import timezone

from django.db import models

# Create your models here.
class Location(models.Model):
    locationId = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

class ImageContent(models.Model):
    thumbResUrl = models.CharField(max_length=300)
    thumbResWidth = models.IntegerField()
    thumbResHeight = models.IntegerField()
    lowResUrl = models.CharField(max_length=300)
    lowResWidth = models.IntegerField()
    lowResHeight = models.IntegerField()
    fullResUrl = models.CharField(max_length=300)
    fullResWidth = models.IntegerField()
    fullResHeight = models.IntegerField()

class VideoContent(models.Model):
    lowResUrl = models.CharField(max_length=300)
    lowResWidth = models.IntegerField()
    lowResHeight = models.IntegerField()
    fullResUrl = models.CharField(max_length=300)
    fullResWidth = models.IntegerField()
    fullResHeight = models.IntegerField()


class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class PostAsJson(models.Model):
    instagramPostId = models.CharField(max_length=50, null=True)
    jsonContent = models.TextField(default="json")


class Post(models.Model):
    TYPES_CONTENT = ( ('PHT', 'photo'), ('VID', 'video') ) # Photo or Video?
    userId = models.IntegerField(null=True)                           # Who scrapped this post?

    # From Instagram post
    contentType = models.CharField(max_length=3, choices=TYPES_CONTENT, default='PHT')
    imageContent = models.OneToOneField(ImageContent, null=True, on_delete=models.CASCADE)
    videoContent = models.OneToOneField(VideoContent, null=True, on_delete=models.CASCADE)
    authorName = models.CharField(max_length=20)
    caption = models.TextField(null=True)
    instagramPostId = models.CharField(max_length=50, unique=True)
    instagramLink = models.CharField(max_length=60, unique=True)
    postedDate = models.DateTimeField(default=None)
    scrappedDate = models.DateTimeField(default=timezone.now)
    likedOrderCnt = models.IntegerField(default=-1)
    location =  models.ForeignKey(Location, null=True) # can be None
    # TODO: migrate to PostgreSQL to handle JSON easily using JSONField
    postAsJson = models.OneToOneField(PostAsJson, null=True, on_delete=models.CASCADE)

    tags = models.ManyToManyField(Tag)
    isScrapped = models.BooleanField(default=False)

    def __str__(self):
        return "id:" + str(id) + ", postId: " +str(self.instagramPostId) + ", scrapped on: " + self.scrappedDate.strftime("%Y-%m-%d %H:%M:%S")
