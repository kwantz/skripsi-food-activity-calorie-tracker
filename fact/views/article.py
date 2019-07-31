import json
from fact.models import Article
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil


@csrf_exempt
def api_article(request):
    if request.method == "GET":
        title = request.GET.get("title", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        articles = Article.objects.all() if title == "" else \
            Article.objects.annotate(lower_title=Lower("title")).filter(lower_title__contains=title.lower())

        total = len(articles)
        pages = ceil(total / 30)
        articles = articles.annotate(published_by=F('user__name'), published_on=F('created_at')) \
            .values('id', 'title', 'author', 'published_on', 'published_by')[offset:limit]

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "articles": list(articles),
        }})

    if request.method == "POST":
        bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
        user = JWT().decode(token)

        if user is None:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        json_request = json.loads(request.body)
        have_data = Article.objects.annotate(lower_title=Lower("title")).filter(lower_title__exact = json_request["title"].lower()).values('id', 'title')

        if len(have_data) > 0:
            return JsonResponse({"message": json_request["title"] + " is already available."}, status=400)

        Article.objects.create(
            user=user,
            title=json_request["title"],
            image=json_request["image"],
            content=json_request["content"],
            author=json_request["author"],
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_article_detail(request, article_id):
    if request.method == "GET":
        article = Article.objects.get(id=article_id)
        return JsonResponse({"results": {
            "title": article.title,
            "image": article.image,
            "author": article.author,
            "content": article.content
        }})

    if request.method == "PUT":
        json_request = json.loads(request.body)
        have_data = Article.objects.annotate(lower_title=Lower("title")).filter(~Q(id=article_id), lower_title__exact = json_request["title"].lower()).values('id', 'title')

        if len(have_data) > 0:
            return JsonResponse({"message": json_request["title"] + " is already available."}, status=400)

        article = Article.objects.get(id=article_id)
        article.title = json_request["title"]
        article.image = json_request["image"]
        article.content = json_request["content"]
        article.author = json_request["author"]
        article.save()

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        article = Article.objects.get(id=article_id)
        article.deleted_at = datetime.now()
        article.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)
