from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm


def user_login(request):
    if request.method == 'POST':
        next_url = request.POST.get('next')
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                id_number=cd['id_number'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(next_url)
                else:
                    return render(request, "login.html",
                                  {"form": form, "status": "red", "message": "حساب شما غیرفعال است."})
            else:
                return render(request, "login.html",
                              {"form": form, "status": "red", "message": "کد ملی یا رمز عبور نامعتبر است."})
    else:
        next_url = request.GET.get('next')
        if next_url is None:
            next_url = 'account:dashboard'

        form = LoginForm(request.GET)
        return render(request, "login.html",
                      {"form": form, "next": next_url})


def user_logout(request):
    logout(request)

    return redirect('account:login')


def home(request):

    return redirect('account:dashboard')


@login_required
def dashboard(request):

    return render(request, "dashboard.html",
                  {"title": "داشبورد"})