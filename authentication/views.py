from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage

# Create your views here.
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})
    
# Email Validation
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry the email is registered in the system. Kindly choose another one '}, status=409)
        return JsonResponse({'email_valid': True})

# User Registration  
class RegistrationView(View):
    def get(self, request):
        return render(request, "authorization/registration.html")
    
    def post(self, request):
        #GET USER DATA FROM FORM
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']  

        context = {
            'fieldValues': request.POST
        }      

        # VALIDATE INPUTS
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password is too short')
                    return render(request, 'authorization/registration.html',context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                email_subject = 'Account Activation'
                email_body = f'Hi {username} and welcome to PesaSave.\n Kindly confirm your email to activate your account.\n Thanks'
                email = EmailMessage(
                    email_subject,
                    email_body,
                    "letscodeit75@gmail.com",
                    [email],
                )
                
                email.send(fail_silently=False)
                messages.success(request, 'Account successfully created')
                return render(request, 'authorization/registration.html')

        return render(request, "authorization/registration.html")
