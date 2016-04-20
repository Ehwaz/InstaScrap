from django.contrib import admin

# Register your models here.
from .models import Post, ImageContent, VideoContent, PostAsJson, Location, Tag

admin.site.register(Post)
admin.site.register(ImageContent)
admin.site.register(VideoContent)
admin.site.register(PostAsJson)
admin.site.register(Location)
admin.site.register(Tag)
