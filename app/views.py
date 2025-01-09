
from django.shortcuts import (
    render,
    redirect,
    HttpResponse,
)
from django.core.serializers import serialize
from django.http import (
    JsonResponse,
)
from django.urls import reverse
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate,
    update_session_auth_hash,
    get_user_model,
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
)
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from app.forms import (
    LoginForm,
    RegisterForm,
    ProfileForm,
    SetNewPasswordForm,
)
from app.models import (
    Order,
)
from app.permissions import (
    login_required,
    own_order_required,
)


User = get_user_model()

@login_required
def index(request):
    return HttpResponse('')


def login(request):

    if request.user.is_authenticated:
        return redirect(reverse('index'))
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(
                request,
                username = username,
                password = password
            )

            if user is not None:
                django_login(request, user)
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
        else:
            print('form is not valid')
            print(form.errors)
        return redirect(reverse('login'))
    
    return render(request, 'login.html', {
        'form': LoginForm()
    })


def logout(request):

    next_url = request.GET.get('next', reverse('index'))

    if request.user.is_authenticated:
        django_logout(request)

    return redirect(next_url)


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():
            
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            
            messages.success(request, "Register successfully!")

            return redirect(reverse('login'))

    form = RegisterForm()

    return render(request, 'register.html', {
        'form': form,
    })


@login_required
def profile(request):

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Updated successfully!")
            return redirect('profile')
        
    form = ProfileForm(instance=request.user)

    return render(request, 'profile.html', {
        'form': form,
    })


@login_required
def change_password(request):

    if request.method == 'POST':

        form = PasswordChangeForm(
            user = request.user,
            data = request.POST,
        )

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Changed successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the error.")

    form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {
        'form': form,
    })


def forget_password(request):

    if request.method == 'POST':

        form = PasswordResetForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(
                    request,
                    "No user is associated with this email address.",
                )
            except User.MultipleObjectsReturned:
                messages.error(
                    request,
                    "Multiple accounts found with this email.",
                )
            else:
                subject = "Password Reset Requested"
                email_template_name = "password_reset_email.html"

                context = {
                    "email": user.email,
                    "domain": request.get_host(),
                    "site_name": "Your Site",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    "protocol": "http",
                }

                email_content = render_to_string(
                    email_template_name,
                    context,
                )

                send_mail(
                    subject,
                    email_content,
                    "noreply@yoursite.com",
                    [user.email]
                )
                
                messages.success(request, "Password reset email has been sent!")
                
                return redirect('login')

    form = PasswordResetForm()

    return render(request, 'forget_password.html', {
        'form': form,
    })


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                return HttpResponse('Password reset successfully.')
        else:
            form = SetNewPasswordForm()
        return render(request, 'reset_password.html', {
            'form': form,
        })
    else:
        messages.error(request, "Link is invalid or has expired.")
        return redirect('password_reset')


@login_required
@own_order_required
def api_order_detail(request, order_id):
    orders = Order.objects.filter(
        user = request.user,
        id = order_id,
    )
    return HttpResponse(serialize('json', orders))
