from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from users.forms import CustomUserCreationForm
# Create your views here.

def signup(request):
	if request.method == "POST":
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)

			return redirect('home')
	else:
		form = CustomUserCreationForm()

	args = {'form': form}

	return render(request,'registration/signup.html', args)