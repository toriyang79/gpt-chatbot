from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} 계정이 생성되었습니다.')
            login(request, user)
            return redirect('chat:index')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})
