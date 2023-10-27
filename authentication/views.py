from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError #Help us create formats that can easily be transferable over a network
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode # Used to encode and decode the user id
from django.contrib.sites.shortcuts import get_current_site #Helps in constructing a domain i.e. a path to our web server
from .utils import account_activation_token # Imports the Token Generator created in the utils.py file
from django.urls import reverse # Will help in reverting the user to the system when they click on the activation link

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
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Account Activation'

                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage(
                    email_subject,
                    'Hi '+user.username + '. Welcome to PesaSave.\n Please usethe link below to activate your account \n'+activate_url,
                    'noreply@letscode.com',
                    [email],
                )
                email.send(fail_silently=False)
                messages.success(request, 'Account successfully created')
                return render(request, 'authorization/registration.html')

        return render(request, "authorization/registration.html")

# Account Verification View
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'The user account is already activated!!')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'You have activated your account successfully.')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')

# User Login View
class LoginView(View):
    def get(self, request):
        return render(request, 'authorization/login.html')
    