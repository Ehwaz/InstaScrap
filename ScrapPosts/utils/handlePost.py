from django.utils import timezone
from datetime import datetime
from django.db import transaction
from ScrapPosts.models import Post, ImageContent, VideoContent, PostAsJson, Location, Tag
import re

@transaction.atomic
def createSavePost(post, scrappedUserId):
    if post is None:
        return None

    if Post.objects.filter(instagramPostId=post['id']).exists():
        return None
    else:
        postAsJsonObject = PostAsJson(instagramPostId = post['id'], jsonContent = post)
        postAsJsonObject.save()

        locationObject = None
        contentJsonNode = post.get('location', None)
        if contentJsonNode is not None:
            locationObject = Location( id = post['location']['id'],
                                name = post['location']['name'],
                                latitude = post['location']['latitude'],
                                longitude = post['location']['longitude'] )
            locationObject.save()

        type = "photo"
        contentJsonNode = post['images']
        imageContentObject = ImageContent( thumbResUrl = contentJsonNode['thumbnail']['url'],
                                           thumbResWidth = contentJsonNode['thumbnail']['width'],
                                           thumbResHeight = contentJsonNode['thumbnail']['height'],
                                           lowResUrl =  contentJsonNode['low_resolution']['url'],
                                           lowResWidth = contentJsonNode['low_resolution']['width'],
                                           lowResHeight = contentJsonNode['low_resolution']['height'],
                                           fullResUrl =  contentJsonNode['standard_resolution']['url'],
                                           fullResWidth = contentJsonNode['standard_resolution']['width'],
                                           fullResHeight = contentJsonNode['standard_resolution']['height'] )
        imageContentObject.save()

        videoContentObject = None
        if post['type'] is "video":
            type = "video"
            contentJsonNode = post['videos']
            videoContentObject = VideoContent( lowResUrl =  contentJsonNode['low_resolution']['url'],
                                           lowResWidth = contentJsonNode['low_resolution']['width'],
                                           lowResHeight = contentJsonNode['low_resolution']['height'],
                                           fullResUrl =  contentJsonNode['standard_resolution']['url'],
                                           fullResWidth = contentJsonNode['standard_resolution']['width'],
                                           fullResHeight = contentJsonNode['standard_resolution']['height'] )
            videoContentObject.save()

        # Associated one-to-one models must be saved ahead.
        postObject = Post(  userId = scrappedUserId,
                            contentType = type,
                            imageContent = imageContentObject,
                            videoContent = videoContentObject,
                            authorName = post['user']['username'],
                            instagramPostId = post['id'],
                            instagramLink = post['link'],
                            postedDate = timezone.make_aware(datetime.fromtimestamp(float(post['created_time'])), timezone.get_current_timezone()),
                            scrappedDate = timezone.now(),
                            postAsJson = postAsJsonObject,
                            isScrapped = False, )
                            #tag = (many-to-many)
        if locationObject is not None:
            postObject.location = locationObject
        if post.get('caption', None) is not None:
            postObject.caption = caption = post['caption']['text']

        postObject.save()

    return postObject

@transaction.atomic
def createSavePostList(postsByJson, scrappedUserId):
    if postsByJson is None:
        return []

    postList = []
    for post in reversed(postsByJson):
        if Post.objects.filter(instagramPostId=post['id']).exists():
            postList.append(Post.objects.get(instagramPostId=post['id']))
        else:
            postAsJsonObject = PostAsJson(instagramPostId = post['id'], jsonContent = post)
            postAsJsonObject.save()

            locationObject = None
            contentJsonNode = post.get('location', None)
            if contentJsonNode is not None:
                locationObject = Location( id = post['location']['id'],
                                    name = post['location']['name'],
                                    latitude = post['location']['latitude'],
                                    longitude = post['location']['longitude'] )
                locationObject.save()

            type = "photo"
            contentJsonNode = post['images']
            imageContentObject = ImageContent( thumbResUrl = contentJsonNode['thumbnail']['url'],
                                               thumbResWidth = contentJsonNode['thumbnail']['width'],
                                               thumbResHeight = contentJsonNode['thumbnail']['height'],
                                               lowResUrl =  contentJsonNode['low_resolution']['url'],
                                               lowResWidth = contentJsonNode['low_resolution']['width'],
                                               lowResHeight = contentJsonNode['low_resolution']['height'],
                                               fullResUrl =  contentJsonNode['standard_resolution']['url'],
                                               fullResWidth = contentJsonNode['standard_resolution']['width'],
                                               fullResHeight = contentJsonNode['standard_resolution']['height'] )
            imageContentObject.save()

            videoContentObject = None
            if post['type'] is "video":
                type = "video"
                contentJsonNode = post['videos']
                videoContentObject = VideoContent( lowResUrl =  contentJsonNode['low_resolution']['url'],
                                               lowResWidth = contentJsonNode['low_resolution']['width'],
                                               lowResHeight = contentJsonNode['low_resolution']['height'],
                                               fullResUrl =  contentJsonNode['standard_resolution']['url'],
                                               fullResWidth = contentJsonNode['standard_resolution']['width'],
                                               fullResHeight = contentJsonNode['standard_resolution']['height'] )
                videoContentObject.save()

            # Associated one-to-one models must be saved ahead.
            postObject = Post(  userId = scrappedUserId,
                                contentType = type,
                                imageContent = imageContentObject,
                                videoContent = videoContentObject,
                                authorName = post['user']['username'],
                                instagramPostId = post['id'],
                                instagramLink = post['link'],
                                postedDate = datetime.fromtimestamp(float(post['created_time'])),
                                scrappedDate = timezone.now(),
                                likedOrderCnt = -1,             # value is assigned after crawling is done.
                                postAsJson = postAsJsonObject,
                                isScrapped = True, )
                                #tag = (many-to-many)
            if locationObject is not None:
                postObject.location = locationObject
            if post.get('caption', None) is not None:
                postObject.caption = caption = post['caption']['text']

            postObject.save()
            postList.append(postObject)

    postList.reverse()
    return postList


#def addLinkToCaption(caption):
#   TODO: replace '@..' to Instagram user link and '#..' to Instagram Tag link.