import json
import requests

from ScrapPosts.models import Post
from ScrapPosts.utils.handlePost import createSavePost
from ScrapPosts.utils.menuList import MenuList

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.csrf import csrf_protect

def login(request):
    template = loader.get_template('ScrapPosts/login.html')
    context = {
        'menuList'  : MenuList.getList(),
        'whichMenu' : 'Login',
        'user'       : request.user,
    }
    return HttpResponse(template.render(context, request))

def logout(request):
    auth_logout(request)
    return redirect('/scrap_posts/login/')

@login_required(login_url='/scrap_posts/login/')
def scrapped_posts(request):
    pageSize = 9
    rowSize = 3
    postList = []

    postList += Post.objects.all().filter(isScrapped=True).order_by('-likedOrderCnt')[:pageSize]
    pagesToRender_2d = [postList[i:i+rowSize] for i in range(0, len(postList), rowSize)]

    # Render
    template = loader.get_template('ScrapPosts/scrapped_posts.html')
    context = {
        'menuList'  : MenuList.getList(),
        'whichMenu' : 'Scrapped Posts',
        'user'       : request.user,
        'liked_posts_2d' : pagesToRender_2d,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/scrap_posts/login/')
def crawl_posts(request):
    numOfPostOnce = 33      # Maximum number of posts returned by API. tested on apigee.com

    latestInstagramPostId = None
    latestlikedOrderCnt = None
    if Post.objects.all().count() > 0:
        lastestSavedPost = Post.objects.all().order_by('-likedOrderCnt')[0]
        latestInstagramPostId = lastestSavedPost.instagramPostId
        latestlikedOrderCnt = lastestSavedPost.likedOrderCnt

    userSocialAuth = request.user.social_auth.get(provider='instagram')
    access_token = userSocialAuth.extra_data.get('access_token')

    queryString = 'https://api.instagram.com/v1/users/self/media/liked?access_token=' + access_token
    queryString += '&count=' + str(numOfPostOnce)

    postList = []
    dbAlreadyHasPost = False
    while dbAlreadyHasPost is False and queryString is not None:
        response = requests.get(queryString)
        if response.status_code is 200:
            responseJson = response.json()
            queryString = responseJson.get('pagination').get('next_url', None)
            postJson = responseJson.get('data', None)

            if postJson is not None and len(postJson) > 0:
                for post in postJson:
                    post['id'] = post['id'].split("_")[0]
                    if post['id'] == latestInstagramPostId:
                        dbAlreadyHasPost = True
                        break
                    else:
                        saveResult = createSavePost(post, request.user.id)
                        if saveResult is not None:
                            postList.append(saveResult)
                        else:
                            dbAlreadyHasPost = True        # post already in DB
                            break
            else:
                print("postJson is None!")
                break
        else:
            print("Response code: " + str(response.status_code) + "\n" + str(response.content))
            break

    baseLikedOrderCnt = 1
    if latestlikedOrderCnt is not None:
        baseLikedOrderCnt = latestlikedOrderCnt+1

    for savedPost in reversed(postList):
        savedPost.likedOrderCnt = baseLikedOrderCnt
        savedPost.save()
        baseLikedOrderCnt += 1

    return redirect('/scrap_posts/liked_posts/')

@login_required(login_url='/scrap_posts/login/')
def liked_posts(request):
    pageSize = 9
    rowSize = 3
    postList = []

    postList += Post.objects.all().order_by('-likedOrderCnt')[:pageSize]
    pagesToRender_2d = [postList[i:i+rowSize] for i in range(0, len(postList), rowSize)]

    # Render
    template = loader.get_template('ScrapPosts/liked_posts.html')
    context = {
        'menuList'  : MenuList.getList(),
        'whichMenu' : 'Liked Posts',
        'user'       : request.user,
        'liked_posts_2d' : pagesToRender_2d,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/scrap_posts/login/')
def submit_access_token(request):
    userSocialAuth = request.user.social_auth.get(provider='instagram')
    access_token = userSocialAuth.extra_data['access_token']
    template = loader.get_template('ScrapPosts/submit_access_token.html')
    context = {
        'menuList'  : MenuList.getList(),
        'whichMenu' : 'Login',
        'user'       : request.user,
        'access_token': access_token,
    }
    return HttpResponse(template.render(context, request))

def set_access_token(request):
    # 'name' attribute: the identifier used in the POST or GET call that happens on form submission
    # 'id' attribute: It is used whenever you need to address a particular HTML element with CSS, JavaScript or a fragment identifier.
    new_access_token = request.POST['access_token']
    userSocialAuth = request.user.social_auth.get(provider='instagram')
    userSocialAuth.extra_data['access_token'] = new_access_token
    userSocialAuth.save()
    return HttpResponseRedirect(reverse('ScrapPosts:submit_access_token'))

def get_post(request):
    returnJson = {'result' : "No posts found."}
    if request.is_ajax() and request.GET:
        try:
            postId = request.GET.get('instagramPostId')
            post = Post.objects.get(instagramPostId = postId)

            returnJson['result'] = "Success"
            returnJson['authorName'] = post.authorName
            returnJson['caption'] = post.caption
            returnJson['instagramPostId'] = postId
            returnJson['instagramLink'] = post.instagramLink
            returnJson['fullResUrl'] = post.imageContent.fullResUrl
            returnJson['fullResWidth'] = post.imageContent.fullResWidth
            returnJson['fullResHeight'] = post.imageContent.fullResHeight
            returnJson['isScrapped'] = post.isScrapped
        except:
            print("get_post: No posts found!")
    return HttpResponse(json.dumps(returnJson), content_type="application/json")

def load_more_posts(request):
    returnJson = {}
    if request.is_ajax() and request.GET:
        try:
            lastPostId = request.GET.get('lastPostId')
            whichPost = request.GET.get('whichPost')

            newRowList = []
            pageSize = 6
            queriedPageSize = pageSize + 1
            rowSize = 3

            lastPost = Post.objects.get(instagramPostId = lastPostId)
            newRowList = Post.objects.all().filter(likedOrderCnt__lt=lastPost.likedOrderCnt)
            if whichPost == 'scrapped':
                newRowList = newRowList.filter(isScrapped=True)
            newRowList = newRowList.order_by('-likedOrderCnt')[:pageSize]

            rowNum = int(len(newRowList)/rowSize)
            for i in range(0, rowNum):
                returnJson[i] = {}
                for j in range(0, rowSize):
                    content = {}
                    content["instagramPostId"] = newRowList[i*rowSize+j].instagramPostId
                    content["fullResUrl"] = newRowList[i*rowSize+j].imageContent.fullResUrl
                    returnJson[i][j] = content

        except:
            print("load_more_posts: No request parameters found!")

    return HttpResponse(json.dumps(returnJson), content_type="application/json")

@csrf_protect
def change_scrap_state(request):
    result = { 'result_state': 'wrong'}
    if request.is_ajax() and request.POST:
        try:
            postId = request.POST.get('postId')
            neweState = request.POST.get('state')
            curPostObj = Post.objects.get(instagramPostId=postId)

            # Check if given state parameter is right.
            if neweState == 'on':
                # Before changing state to 'on', post's state must be 'off'.
                if curPostObj.isScrapped is True:
                    print("change_scrapt_state: wrong post state: 'scrapped'")
                else:
                    curPostObj.isScrapped = True
                    curPostObj.save()
                    result['result_state'] = 'on'
            elif neweState == 'off':
                # Before changing state to 'off', post's state must be 'on'.
                if curPostObj.isScrapped is False:
                    print("change_scrapt_state: wrong post state: 'not scrapped'")
                else:
                    curPostObj.isScrapped = False
                    curPostObj.save()
                    result['result_state'] = 'off'
        except:
            print("change_scrap_state: No request parameters found!")

    return HttpResponse(json.dumps(result), content_type="application/json")