from django.urls import path
from . import views, feeds

app_name = 'blog'

urlpatterns = [
    path("", views.post_list, name="list"),
    path("<int:year>/<int:month>/<int:day>/<slug:post>/",
        views.post_detail, name="detail"),
    path('tag/<slug:tag_slug>/', views.post_list, name="list_by_tag"),
    path('feed/', feeds.LatestPostFeed(), name="feed")
]