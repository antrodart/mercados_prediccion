from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from users.forms import SignupForm, EditProfileForm, LoginForm
from users.models import User
from mercados_de_prediccion.utils import add_months
import datetime

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
		form = SignupForm(request.POST, request.FILES)
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
		raise PermissionDenied(_("Must be logged as Admin."))
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
	user = User.objects.get(id=request.user.id)
	if not user == request.user:
		raise PermissionDenied(_("You cannot edit other user's profile."))
	if request.method == "POST":
		if request.POST.get('delete') is not None:
			user.deletion_date = add_months(datetime.date.today(), 1)
			user.save()
			return redirect('/user/?userId='+str(user.pk))

		form = EditProfileForm(request.POST, request.FILES, instance=user)
		if form.is_valid():
			form.save()

			return redirect('/user/?userId='+str(user.pk))
	else:
		form = EditProfileForm(instance=user)

	args = {'form': form, 'model': user}

	return render(request, 'user/edit_profile.html', args)


@login_required()
def change_password(request):
	if request.method == "POST":
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			updated = True
			msg =  _('Your password was successfully updated')

		else:
			updated = False
			msg = _('Please correct the error below.')
	else:
		msg = None
		updated = False
		form = PasswordChangeForm(request.user)

	args = {'form': form, 'user_id': request.user.pk, 'user_slug': request.user.slug, 'msg':msg, 'updated': updated}
	return render(request, 'user/change_password.html', args)
