from django.shortcuts import render

# Create your views here.from .models import Post

from .models import Post

def home(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})
