from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .forms import UserRegisterForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserProfileForm


@login_required
def view_user_profile(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'avatar_url': user.avatar.url if user.avatar else None
    })


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})


def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль обновлён')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile_page.html', {'form': form})

