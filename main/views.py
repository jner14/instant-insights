from django.shortcuts import render, get_object_or_404, redirect
# from django.utils import timezone

# from .models import Post
# from .forms import PostForm

# Create your views here.


def home(request):
    return render(request, 'main/home.html', {})
