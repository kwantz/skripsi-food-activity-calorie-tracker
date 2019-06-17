from fact.models import Quote, Article
from django.http import JsonResponse
from django.db.models import F


def api_member_newsfeed(request):
    if request.method == "GET":
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        quotes = Quote.objects.all().order_by('-created_at')
        quotes = quotes.values('id', 'desc', 'author')[offset:limit]

        articles = Article.objects.all().order_by('-created_at')
        articles = articles.annotate(published_on=F('created_at')) \
            .values('id', 'title', 'author', 'content', 'image', 'published_on')[offset:limit]

        return JsonResponse({"results": {
            "quotes": list(quotes),
            "articles": list(articles),
        }})

    return JsonResponse({"message": "Not Found"}, status=404)
