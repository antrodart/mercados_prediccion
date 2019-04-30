from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from users.forms import SignupForm, EditProfileForm, LoginForm
from users.models import CustomUser


def login_view(request):
	if not request.user.is_anonymous:
		return redirect ('home')
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			user = form.login(request)
			if user:
				login(request, user)
				return redirect('home')
	else:
		form = LoginForm()

	args = {'form': form}
	return render(request,'registration/login.html', args)


def signup(request):
	if not request.user.is_anonymous:
		return redirect ('home')
	if request.method == "POST":
		form = SignupForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(email=email, password=raw_password)
			login(request, user)

			return redirect('home')
	else:
		form = SignupForm()

	args = {'form': form, 'language_format':'dd/mm/yyyy'}

	return render(request,'registration/signup.html', args)


@login_required()
def create_admin(request):
	if not request.user.is_staff:
		raise PermissionDenied("Must be logged as Admin.")
	if request.method == "POST":
		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.is_staff = True
			user.save()

			return redirect('home')
	else:
		form = SignupForm()

	args = {'form': form, 'admin_creation': True}

	return render(request, 'registration/signup.html', args)



@login_required()
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