# Create your views here


from django.shortcuts import render, get_object_or_404
from .models import Post

def home(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'blog/index.html', {'posts': posts})

def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    return render(request, 'blog/post_detail.html', {'post': post})
