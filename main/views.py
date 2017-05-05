from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
# from django.utils import timezone

# from .models import Post
# from .forms import PostForm

# Create your views here.

@xframe_options_exempt
def home(request):
    return render(request, 'main/home.html', {})
