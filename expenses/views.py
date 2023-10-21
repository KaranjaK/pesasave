from django.shortcuts import render, HttpResponse

# Create your views here.
def HomeView(request):
    return render(request, 'base.html')