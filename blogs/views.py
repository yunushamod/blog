from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailForm, CommentForm
from django.contrib import messages
from taggit.models import Tag
from django.db.models import Count


# Create your views here.


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])       
    paginator = Paginator(object_list, 10) # 10 posts in each page
    page = request.GET.get('page')
    try:
      posts = paginator.page(page)
    except PageNotAnInteger:
      # if page is not an integer deliver the first page
      posts = paginator.page(1)
    except EmptyPage:
      # if the page requested is out of range deliver the last page of results
      posts = paginator.page(paginator.num_pages) # last page
    return render(request, "blog/list.html", {'posts': posts,
     'page':page, 'tag':tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
      publish__year=year, publish__month=month,
      publish__day=day)
    comments = post.comments.filter(active=True)
    share_form = EmailForm()
    comment_form = CommentForm()
    sent = False
    if request.method == "POST":
          if request.POST.get("multipleForm") == "shareForm":
                share_form = EmailForm(request.POST)
                if share_form.is_valid():
                      cd = share_form.cleaned_data
                      post_url = request.build_absolute_uri(
                        post.get_absolute_url()
                      )
                      subject = f"{cd['name']} {cd['email']} recommends you read {post.title}"
                      message = f"Read {post.title} at {post_url}\n\n {cd['name']}'s comment: {cd['comments']}"
                      send_mail(subject, message, 'admin@myblog.com', [cd['to']])
                      sent=True
                      messages.info(request, "Email was successfully sent")
                      return redirect(request.build_absolute_uri(post.get_absolute_url()))
          elif request.POST.get("multipleForm") == "commentForm":
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                      # Create comment object but not saved to database
                      new_comment = comment_form.save(commit=False)
                      # Add the current post to the comment
                      new_comment.post = post
                      new_comment.save()
                      messages.info(request, "Comment added successfully")
                      return redirect(request.build_absolute_uri(post.get_absolute_url()))
    # else:
    #       share_form = EmailForm()
    #       comment_form = CommentForm()
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, "blog/detail.html", 
    {'post':post, "share_form":share_form, 'comment_form':comment_form, 'comments':comments,
    'similar_posts':similar_posts})

   