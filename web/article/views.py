from django.shortcuts import render

from .models import Article


# Create your views here.
def index(request):
    article_list = Article.objects.order_by('-pub_time')
    context = {
        'article_list': article_list,
    }
    return render(request=request, template_name='index.html', context=context)
