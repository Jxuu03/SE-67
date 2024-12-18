import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from .models import *
from .forms import UserRegisterForm  # Ensure you have this form
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password


## -- Authen -- ##
class SignUpView(CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy("login")
    template_name = "events/signup.html"

    def form_valid(self, form):
        member = form.save(commit=False)
        member.save()
        Member.objects.create(
            email=member.email,
            username=member,
        )

        # Log in the user immediately
        auth_login(self.request, member)
        return super().form_valid(form)


class UserLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = "events/login.html"
    success_url = reverse_lazy("home")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


# Reset password
def resetPassword(request):
    verification_codes = request.session.get("verification_codes", {})

    if request.method == "POST":
        data = json.loads(request.body)
        step = data.get("step")

        # Step 1: Send the code to user's email
        if step == "1":
            email = data.get("email")
            try:
                user = User.objects.get(email=email)  # Check if the user exists

                # Generate a 6-digit code
                code = get_random_string(6, allowed_chars="0123456789")
                verification_codes[email] = code
                request.session["verification_codes"] = verification_codes
                print(f'-------------------- {code}')

                # Send code via email
                send_mail(
                    "Password Reset Code",
                    f"Your password reset code is: {code}",
                    settings.DEFAULT_FROM_EMAIL, 
                    [email],
                    fail_silently=False,
                )
                return JsonResponse(
                    {"status": "success", "message": "Code sent successfully."}
                )
            except Member.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Email not found."})
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                return JsonResponse(
                    {"status": "error", "message": "Failed to send email"}
                )

        # Step 2: Verify the code
        elif step == "2":
            email = data.get("email")
            code = data.get("code")

            if verification_codes.get(email) == code:
                return JsonResponse(
                    {"status": "success", "message": "Code verified successfully."}
                )
            else:
                return JsonResponse({"status": "error", "message": "Invalid code."})

        # Step 3: Reset the password
        elif step == "3":
            email = data.get("email")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")

            if new_password == confirm_password:
                user = get_object_or_404(Member, email=email)
                user.password = make_password(new_password)
                user.save()
                
                auth_user = get_object_or_404(User, email=email)
                auth_user.password = make_password(new_password)
                auth_user.save()

                # Remove the code from the session after successful password reset
                verification_codes.pop(email, None)
                request.session["verification_codes"] = verification_codes

                return JsonResponse(
                    {"status": "success", "message": "Password reset successfully."}
                )
            else:
                return JsonResponse(
                    {"status": "error", "message": "Passwords do not match."}
                )

    return render(request, "events/resetpass.html")


# ----- For Content ----- #

def home(request):
    return render(request, "events/home.html")
