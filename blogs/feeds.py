from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Post

class LatestPostFeed(Feed):
    title="Yunus' blog"
    link = reverse_lazy('blog:list')
    description = 'New posts of blog.'

    def items(self):
        return Post.published.all()[:10]
    def item_title(self, obj):
        return obj.title
    def item_description(self, obj):
        return truncatewords(obj.body, 30)

