# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings 
import random
import datetime

from .forms import UserSignUpForm, EmailOTPForm
from .models import User

def generate_otp():
    """Generates a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Sends the generated OTP to the user's email."""
    subject = 'Your EduStream Login OTP'
    message = (
        f'Dear User,\n\n'
        f'Your One-Time Password (OTP) for EduStream login is: {otp}\n\n'
        f'This OTP is valid for 5 minutes. Please do not share it with anyone.\n\n'
        f'If you did not request this OTP, please ignore this email.'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edustream.com')
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"OTP email sent to {email}") 
    except Exception as e:
        print(f"Failed to send OTP email to {email}: {e}")
def signup_view(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'There was an error with your submission. Please correct the highlighted fields.')
    else:
        form = UserSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    """Handles user login and initiates 2FA OTP process."""
    if request.user.is_authenticated:
        # Redirect authenticated users
        if request.user.user_type == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # User authenticated, now send OTP for 2FA
                otp = generate_otp()
                user.email_otp = otp
                user.otp_created_at = timezone.now()
                user.save()
                send_otp_email(user.email, otp)
                # Store user ID in session temporarily for OTP verification
                request.session['user_id_for_otp'] = user.id
                messages.info(request, 'An OTP has been sent to your email. Please enter it to complete your login.')
                return redirect('verify_otp')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def verify_otp_view(request):
    """Handles 2FA OTP verification."""
    user_id = request.session.get('user_id_for_otp')

    if not user_id:
        messages.error(request, 'Authentication session expired or invalid. Please log in again.')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        # Clear the session key if user doesn't exist to prevent looping
        if 'user_id_for_otp' in request.session:
            del request.session['user_id_for_otp']
        return redirect('login')

    if request.method == 'POST':
        form = EmailOTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            if user.email_otp == entered_otp:
                # Check OTP expiry (5 minutes)
                if user.otp_created_at and (timezone.now() - user.otp_created_at) < datetime.timedelta(minutes=5):
                    # OTP is valid and not expired
                    user.email_otp = None  # Clear OTP after successful verification
                    user.otp_created_at = None
                    user.save()
                    login(request, user) # Log the user in
                    del request.session['user_id_for_otp'] # Clear temporary session key
                    messages.success(request, 'Login successful!')
                    if user.user_type == 'teacher':
                        return redirect('teacher_dashboard')
                    else:
                        return redirect('student_dashboard')
                else:
                    messages.error(request, 'OTP expired. Please try logging in again.')
                    # Clear session key to force new login process
                    if 'user_id_for_otp' in request.session:
                        del request.session['user_id_for_otp']
                    return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        # If form is not valid, errors are displayed by the template
    else:
        form = EmailOTPForm()

    return render(request, 'registration/verify_otp.html', {'form': form, 'email': user.email})


def logout_view(request):
    """Logs out the current user."""
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')