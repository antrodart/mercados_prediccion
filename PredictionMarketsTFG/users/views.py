from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from users.forms import SignupForm, EditProfileForm
from users.models import CustomUser
# Create your views here.

def signup(request):
	if request.method == "POST":
		form = SignupForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)

			return redirect('home')
	else:
		form = SignupForm()

	args = {'form': form}

	return render(request,'registration/signup.html', args)


def edit_profile(request):
	customUser = CustomUser.objects.get(id=request.user.id)
	if request.method == "POST":
		form = EditProfileForm(request.POST, instance=customUser)
		if form.is_valid():
			form.save()

			return redirect('home')
	else:
		form = EditProfileForm(instance=customUser)

	args = {'form': form, 'model': customUser}

	return render(request, 'editProfile.html', args)