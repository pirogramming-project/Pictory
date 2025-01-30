from django.shortcuts import render

def login(request):
    return render(request, 'users/login.html')

def signup(request):
    return render(request, 'users/signup.html')

def main(request):
    return render(request, 'users/main.html')

