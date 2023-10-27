from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

#This is the home page view
@login_required(login_url='/authentication/login/')
def HomeView(request):
    return render(request, 'base.html')