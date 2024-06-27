from django.shortcuts import render, redirect, get_object_or_404
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login as auth_login, authenticate
from django.core.files.storage import FileSystemStorage
from .forms import CustomUserCreationForm
from .models import PrivateChatRoom

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if file:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            return Response({'file_url': file_url, 'csrf_token': get_token(request)})
        else:
            return Response({'error': 'No file found'}, status=400)



def login(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user, created = User.objects.get_or_create(username=username)
            auth_login(request, user)
            return redirect('choice')
    else:
        form = CustomUserCreationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
    

def choice(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'choice.html')

def chatroom(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'chatroom.html')

def private_chat(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'private_chat.html')


