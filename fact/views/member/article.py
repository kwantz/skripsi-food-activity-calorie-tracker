from fact.models import Article
from django.http import JsonResponse
from django.db.models import F


def api_member_article(request):
    if request.method == "GET":
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        articles = Article.objects.all().order_by('-created_at')
        articles = articles.annotate(published_on=F('created_at')) \
            .values('id', 'title', 'author', 'content', 'image', 'published_on')[offset:limit]

        return JsonResponse({"results": {
            "articles": list(articles),
        }})

    return JsonResponse({"message": "Not Found"}, status=404)

def api_member_article_detail(request, article_id):
    if request.method == "GET":
        article = Article.objects.get(id=article_id)
        return JsonResponse({"results": {
            "title": article.title,
            "image": article.image,
            "author": article.author,
            "content": article.content,
            "published_on": article.created_at
        }})

    return JsonResponse({"message": "Not Found"}, status=404)
