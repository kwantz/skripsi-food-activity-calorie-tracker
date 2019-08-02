from fact.models import Article, ArticleView
from django.http import JsonResponse
from django.db.models import F
from fact.libraries.jwt import JWT


def api_member_article(request):
    if request.method == "GET":
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        articles = Article.objects.all().order_by('-created_at')
        articles = articles.annotate(published_on=F('created_at')) \
            .values('id', 'title', 'author', 'content', 'image', 'published_on')[offset:limit]

        results = []
        for article in articles:
            # view = ArticleView.objects.filter(article=article)
            results.append({
                "id": article['id'],
                "title": article['title'],
                "author": article['author'],
                "content": article["content"],
                "image": article["image"],
                "published_on": article["published_on"],
                # "view": len(view)
            })

        return JsonResponse({"results": {
            "articles": list(articles),
        }})

    return JsonResponse({"message": "Not Found"}, status=404)


def api_member_article_detail(request, article_id):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        article = Article.objects.get(id=article_id)
        view = ArticleView.objects.filter(article=article)

        ArticleView.objects.create(
            article=article,
            user=user
        )

        return JsonResponse({"results": {
            "title": article.title,
            "image": article.image,
            "author": article.author,
            "content": article.content,
            "published_on": article.created_at,
            "view": len(view)
        }})

    return JsonResponse({"message": "Not Found"}, status=404)
