from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import random

# Temporary storage for verification codes (better to use a model in production)
verification_codes = {}

def send_verification_code(email):
    """Generate and send a verification code to the given email."""
    code = random.randint(100000, 999999)
    verification_codes[email] = code
    send_mail(
        "Your Verification Code",
        f"Your verification code is {code}.",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False
    )

def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        if not name or not email:
            return JsonResponse({'message': 'Name and email are required.'}, status=400)

        # Check if the user exists
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            send_verification_code(email)
            return JsonResponse({'message': 'Verification code sent to your email. Please verify.'})
        else:
            # Create a temporary user object with the name
            User.objects.create(username=name, email=email)
            send_verification_code(email)
            return JsonResponse({'message': 'Verification code sent to your email. Complete signup to create an account.'})

    return render(request, 'login.html')

def verify_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = int(request.POST.get('code'))

        if email in verification_codes and verification_codes[email] == code:
            # Check if the user already exists
            user, created = User.objects.get_or_create(email=email)
            if created:
                # Set a default username for new users
                user.set_unusable_password()  # Prevent login without a password
                user.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'message': 'Verification successful.',
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        else:
            return JsonResponse({'message': 'Invalid verification code.'}, status=400)

    return render(request, 'verify.html')
