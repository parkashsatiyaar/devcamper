from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import html
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import tblUser, Role
import random
import os
# Create your views here.


def index(request):
    return render(request, "index.html")

# register route


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            role = request.POST.get('role')
            password = request.POST.get('password')
            confirm_password = request.POST['confirm_password']
            if password == confirm_password:
                if User.objects.filter(username=username).exists():
                    messages.info(request, 'User Already exist')
                    return redirect('register')
                else:
                    if User.objects.filter(email=email).exists():
                        messages.info(request, 'Email Already exist')
                        return redirect('register')
                    else:
                        request.session['username'] = username
                        request.session['role'] = role
                        request.session['email'] = email
                        request.session['password'] = password
                        otp = []
                        num = str(random.randint(1000, 9999))
                        request.session['otp'] = num
                        for x in num:
                            otp.append(x)
                        context = {'name': username, 'auth_otp': otp}
                        html_content = render_to_string(
                            'accounts/email.html', context)
                        text_content = strip_tags(html_content)

                        send_mail = EmailMultiAlternatives(
                            "Account email verification",
                            text_content,
                            settings.EMAIL_HOST_USER,
                            [email]
                        )
                        send_mail.attach_alternative(html_content, 'text/html')
                        send_mail.send()
                        return redirect('verify')
            messages.info(request, 'password did not match')
            return redirect('login')
    roles = Role.objects.all()
    data = {
        'roles': roles,
    }

    return render(request, 'accounts/register.html', data)


# login route
def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                tbluser = tblUser.objects.get(userid=user.id)
                if tbluser.isdeleted:
                    messages.info(request, "This user has no longer Access")
                    return redirect('login')
                auth.login(request, user)
                try:
                    if len(request.session['page']) != 0:
                        return HttpResponseRedirect(request.session.get('page'))
                except:
                    return redirect('dashboard')
            else:
                messages.info(request, "Invalid Username or Password")
                return redirect('login')

    try:
        request.session['page'] = request.GET.get('next')
    except:
        request.session['page'] = {}
    return render(request, 'accounts/login.html')

# verify route


def verify(request):
    if request.user.is_authenticated:
        return redirect('home')
    try:
        if request.session['username']:
            pass
    except:
        return redirect('home')
    else:
        if request.method == 'POST':
            otp = request.session.get('otp')
            if request.POST.get('auth_otp') == otp:
                user = User.objects.create_user(
                    username=request.session['username'], password=request.session['password'], email=request.session['email'])
                user.save()
                trole = Role.objects.get(id=int(request.session['role']))
                tbluser = tblUser(
                    userid=user, username=request.session['username'], role=trole)
                tbluser.save()
                auth.login(request, user)
                context = {'name': request.session['username']}
                html_content = render_to_string(
                    'accounts/confirm_email.html', context)
                text_content = strip_tags(html_content)

                send_mail = EmailMultiAlternatives(
                    "Registration Successfull",
                    text_content,
                    settings.EMAIL_HOST_USER,
                    [request.session['email']]
                )
                send_mail.attach_alternative(html_content, 'text/html')
                send_mail.send()
                return redirect('dashboard')
            messages.info(request, "Invalid otp or email register again!")
            return redirect('register')
    return render(request, 'accounts/verify.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    tbluser = {}
    try:
        tbluser = tblUser.objects.get(userid=request.user)
    except:
        pass

    data = {
        'user_roles': tbluser
    }
    return render(request, 'accounts/dashbord.html', data)


@login_required(login_url='login')
def profile(request):
    account = User.objects.get(email=request.user.email)
    tbluser = {}
    try:
        tbluser = tblUser.objects.get(userid=request.user)
    except:
        pass
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if len(email) >= 8:
            account.email = email
        if len(password) >= 4:
            account.set_password(password)
        if len(fname) >= 3:
            account.first_name = fname
        if len(lname) >= 3:
            account.last_name = lname
        if len(request.FILES) != 0:
            try:
                os.remove(tbluser.photo.path)
            except:
                pass
            tbluser.photo = request.FILES['photo']
        account.save()
        tbluser.save()
        return redirect('profile')
    data = {
        'account': tbluser
    }

    return render(request, 'accounts/profile.html', data)


@login_required(login_url='login')
def deactivate(request):
    if request.method == "POST":
        tbluser = tblUser.objects.get(userid=request.user)
        tbluser.isdeleted = True
        tbluser.save()
        auth.logout(request)
        return redirect('login')
    else:
        return redirect('home')


def reset_password(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            otp_token = request.POST['otp_token']
            request.session['password'] = password
            request.session['email'] = email
            request.session['otp_token'] = otp_token
            try:
                user = User.objects.get(email=email)
            except:
                user = None
            if user is not None:
                tbluser = tblUser.objects.get(userid=user.id)
                if tbluser.isdeleted:
                    messages.info(request, "This user has no longer Access")
                    return redirect('login')
                otp = []
                num = str(random.randint(1000, 9999))
                request.session['otp1'] = num
                for x in num:
                    otp.append(x)
                context = {'name': email, 'auth_otp': otp}
                html_content = render_to_string(
                    'accounts/email.html', context)
                text_content = strip_tags(html_content)

                send_mail = EmailMultiAlternatives(
                    "Password change verification",
                    text_content,
                    settings.EMAIL_HOST_USER,
                    [email]
                )
                send_mail.attach_alternative(html_content, 'text/html')
                send_mail.send()
                return redirect('reset_verify')
            messages.info(request, "This user has no longer Access")
            return redirect('login')
    return render(request, 'accounts/reset.html')


def reset_verify(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            otp = request.session.get('otp1')
            if request.POST.get('auth_otp') == otp:
                try:
                    user = User.objects.get(
                        email=request.session.get('email'))
                    user.set_password(request.session['password'])
                    user.save()
                    auth.login(request, user)
                except:
                    messages.info(request, "This user has no longer Access")
                    return redirect('login')
                context = {'name': request.session['email']}
                html_content = render_to_string(
                    'accounts/confirm_password.html', context)
                text_content = strip_tags(html_content)

                send_mail = EmailMultiAlternatives(
                    "Password change Alert!",
                    text_content,
                    settings.EMAIL_HOST_USER,
                    [request.session['email']]
                )
                send_mail.attach_alternative(html_content, 'text/html')
                send_mail.send()
                return redirect('dashboard')
            messages.info(request, "Invalid otp or email, reset again!")
            return redirect('login')
    if not request.session.get('otp_token'):
        return redirect('home')
    return render(request, 'accounts/reset_otp.html')
