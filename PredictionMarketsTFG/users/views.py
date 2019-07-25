from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError, transaction
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from users.forms import SignupForm, EditProfileForm, LoginForm, VerifyForm
from users.models import User, VerifyRequest
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
			return redirect('/user/'+str(user.pk)+'/'+str(user.slug()))

		form = EditProfileForm(request.POST, request.FILES, instance=user)
		if form.is_valid():
			form.save()

			return redirect('/user/'+str(user.pk)+'/'+str(user.slug()))
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


@login_required()
def verify_account(request):
	if request.user.is_verified:
		raise PermissionDenied(_("You must not be verified."))
	verify_request = VerifyRequest.objects.filter(user=request.user).first()
	if verify_request and verify_request.is_accepted is None:
		args = {}
		return render(request, 'user/verify_account_sent.html', args)
	elif verify_request and verify_request.is_accepted == False:
		rejected = True
	else:
		rejected = False
	if request.method == "POST":
		form = VerifyForm(request.POST, user=request.user, old_verify_request = verify_request)
		if form.is_valid():
			form.save()

			return redirect('/user/' + str(request.user.pk) + '/' + str(request.user.slug()))
	else:
		form = VerifyForm(user=request.user, old_verify_request=verify_request)

	args = {'form': form, 'rejected': rejected}

	return render(request, 'user/verify_account.html', args)


@login_required()
def list_verify_requests(request):
	if not request.user.is_staff:
		raise PermissionDenied(_("Must be logged as Admin."))

	requests_to_judge = VerifyRequest.objects.order_by('-is_accepted')
	paginator = Paginator(requests_to_judge, per_page=9)
	page = request.GET.get('page')

	try:
		requests = paginator.get_page(page)
	except PageNotAnInteger:
		requests = paginator.get_page(1)
	except EmptyPage:
		requests = paginator.page(paginator.num_pages)

	args = {'requests': requests,}

	return render(request, 'user/list_judge_verify_requests.html', args)


@login_required()
def accept_verify_request(request, verify_request_id):
	if not request.user.is_staff:
		raise PermissionDenied(_("Must be logged as Admin."))
	verify_request = get_object_or_404(VerifyRequest, pk=verify_request_id)
	try:
		with transaction.atomic():
			user = verify_request.user
			verify_request.is_accepted = True
			user.is_verified = True
			verify_request.save()
			user.save()

			return redirect('/verify/list-requests/')
	except IntegrityError:
		return redirect('/verify/list-requests/')


@login_required()
def reject_verify_request(request, verify_request_id):
	if not request.user.is_staff:
		raise PermissionDenied(_("Must be logged as Admin."))
	verify_request = get_object_or_404(VerifyRequest, pk=verify_request_id)
	try:
		with transaction.atomic():
			user = verify_request.user
			verify_request.is_accepted = False
			verify_request.save()

			return redirect('/verify/list-requests/')
	except IntegrityError:
		return redirect('/verify/list-requests/')