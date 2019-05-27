import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import Article
from django.db.models.functions import Lower
from math import ceil

@csrf_exempt
def article_api(request):

    if request.method == "GET":
        title = request.GET.get("title", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        articles = Article.objects.all() if title == "" else \
            Article.objects.annotate(lower_title=Lower("title")).filter(lower_title__contains=title)

        total = len(articles)
        pages = ceil(total / 30)
        articles = articles[offset:limit]

        article_results = []
        for article in articles:
            article_results.append({
                "id": article.id,
                "title": article.title,
                "author": article.author,
                "published_on": article.created_at,
                "published_by": article.user.name
            })

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "articles": article_results,
        }})

    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)
        title = json_request["title"]
        author = json_request["author"]
        image = json_request["image"]
        content = json_request["content"]

        Article.objects.create(
            title=title,
            image=image,
            content=content,
            author=author,
            user=user
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})
