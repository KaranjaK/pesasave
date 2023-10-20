from django.shortcuts import render, HttpResponse

# Create your views here.
def HomeView(request):
    return HttpResponse('<h1>Expense app is workin</h1>')