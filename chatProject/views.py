from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

def index(request):
    return render(request, 'index.html')

def chat(request):
    return render(request, 'chat.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, 'index.html')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')


    return render(request, 'login.html')


def logout_page(request):
    logout(request)
    return redirect('index')




def register_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register-page')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register-page')


        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register-page')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'User created successfully')
            return redirect('login-page')
        
    return render(request, 'registration.html')