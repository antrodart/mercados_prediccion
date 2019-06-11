from django.http import JsonResponse
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _, get_language
from django.forms.formsets import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .forms import *
from users.models import User
from django.views.generic import TemplateView
import datetime
import logging

class HomePageView(TemplateView):
	template_name = 'home.html'


class AboutView(TemplateView):
	template_name = 'about.html'


class ContactView(TemplateView):
	template_name = 'contact.html'


def list_categories_view(request):
	if get_language() == "en":
		order = "title"
	else:
		order = "title_es"
	all_categories = Category.objects.all().order_by(order)
	paginator = Paginator(all_categories, per_page=10)
	page = request.GET.get('page')

	try:
		categories = paginator.get_page(page)
	except PageNotAnInteger:
		categories = paginator.get_page(1)
	except EmptyPage:
		categories = paginator.page(paginator.num_pages)

	args = {'categories': categories}
	logging.info('Listing categories')

	return render(request, 'category/list_categories.html', args)


@login_required()
def create_category_view(request):
	if not request.user.is_staff:
		raise PermissionDenied(_("Must be logged as Admin."))
	if request.method == "POST":
		form = CreateCategoryForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()

			return redirect('categories')
	else:
		form = CreateCategoryForm()

	args = {'form': form}
	return render(request, 'category/create_category.html', args)


@login_required()
def edit_category_view(request):
	if not request.user.is_staff:
		raise PermissionDenied(_("Must be logged as Admin."))
	category_id = request.GET.get('categoryId')
	category = get_object_or_404(Category, pk=category_id)
	if request.method == "POST":
		form = CreateCategoryForm(request.POST, request.FILES, instance=category)
		if form.is_valid():
			form.save()

			return redirect('categories')
	else:
		form = CreateCategoryForm(instance=category)

	args = {'form': form}
	return render(request, 'category/create_category.html', args)


@login_required()
def list_created_groups_view(request):
	created_groups = Group.objects.filter(moderator=request.user.id).order_by('creation_date')
	paginator = Paginator(created_groups, per_page=10)
	page = request.GET.get('page')

	try:
		groups = paginator.get_page(page)
	except PageNotAnInteger:
		groups = paginator.get_page(1)
	except EmptyPage:
		groups = paginator.page(paginator.num_pages)

	args = {'groups': groups, 'view_name': 'list_created'}

	return render(request, 'group/list_groups.html', args)


def list_all_groups_view(request):
	all_groups = Group.objects.filter(is_visible=True).order_by('creation_date')
	paginator = Paginator(all_groups, per_page=10)
	page = request.GET.get('page')

	try:
		groups = paginator.get_page(page)
	except PageNotAnInteger:
		groups = paginator.get_page(1)
	except EmptyPage:
		groups = paginator.page(paginator.num_pages)

	args = {'groups': groups, 'view_name': 'list_all'}

	return render(request, 'group/list_groups.html', args)


@login_required()
def create_group_view(request):
	if request.method == "POST":
		form = CreateGroupForm(request.POST, request.FILES, user=request.user)
		if form.is_valid():
			group = form.save(commit=False)
			is_visible = request.POST.get('is_visible')
			if is_visible:
				group.is_visible = True
			else:
				group.is_visible = False

			group.save()

			joined_group = JoinedGroup(is_accepted=True, user=request.user, group_id=group.pk)
			joined_group.save()

			return redirect('/group/?groupId=' + str(group.pk))
	else:
		form = CreateGroupForm(user=request.user)

	args = {'form': form}
	return render(request, 'group/create_group.html', args)


@login_required()
def edit_group_view(request):
	group_id = request.GET.get('groupId')
	group = get_object_or_404(Group, pk=group_id)
	if not group.moderator == request.user:
		raise PermissionDenied(_("You cannot edit this group."))
	if request.method == "POST":
		if request.POST.get('delete') is not None:
			group.delete()
			return redirect('/groups/created')

		form = CreateGroupForm(request.POST, request.FILES, instance=group, user=request.user)
		if form.is_valid():
			group = form.save(commit=False)
			is_visible = request.POST.get('is_visible')
			if is_visible:
				group.is_visible = True
			else:
				group.is_visible = False

			group.save()

			return redirect('/group/?groupId=' + str(group_id))
	else:
		form = CreateGroupForm(instance=group, user=request.user)

	args = {'form': form, 'editing': True}
	return render(request, 'group/create_group.html', args)


@login_required()
def display_group_view(request):
	group_id = request.GET.get('groupId')
	user = request.user
	group = get_object_or_404(Group, pk=group_id)
	try:
		joined_group = JoinedGroup.objects.get(user=user, group=group)
	except:
		joined_group = None

	user_is_member = False
	if joined_group:
		user_is_member = True

	args = {'group': group, 'user_is_member': user_is_member}

	return render(request, 'group/display_group.html', args)


@login_required()
def create_market_view(request):
	user = User.objects.get(pk=request.user.pk)
	group_id = request.GET.get('groupId')
	if group_id:
		group = get_object_or_404(Group, pk=group_id)
	else:
		group = None

	if group and not group.moderator == user:
		raise PermissionDenied(_("You can't create a market in this group."))
	elif not group and not user.is_staff and not user.is_verified:
		raise PermissionDenied(_("You can't create a public market. Please contact us if you want to verify your account and create public markets."))

	# Create the formset, specifying the form and formset we want to use.
	OptionFormSet = formset_factory(CreateOptionForm, formset=BaseOptionFormSet, min_num=2,max_num=10)

	if request.method == "POST":
		market_form = CreateMarketForm(request.POST, request.FILES, user=request.user, group=group)
		option_formset = OptionFormSet(request.POST)

		if market_form.is_valid():
			if market_form.cleaned_data['is_binary'] == '1':
				market = market_form.save()

				try:
					with transaction.atomic():
						yes_option = Option.objects.create(name='Yes', binary_yes=True, market=market)
						no_option = Option.objects.create(name='No', binary_yes=False, market=market)
						Price.objects.create(option=yes_option, is_yes=True, is_last=True)
						Price.objects.create(option=no_option, is_yes=False, is_last=True)

						return redirect('/market/?marketId=' + str(market.pk))

				except IntegrityError:
					return redirect('/market/?marketId=' + str(market.pk))

			else:
				if option_formset.is_valid():
					# Save market info
					market = market_form.save()

					# Now save the data for each option in the formset
					new_options = []

					for option_form in option_formset:
						name = option_form.cleaned_data.get('name')

						new_options.append(Option(name=name, market=market))

					try:
						with transaction.atomic():
							for option in new_options:
								option.save()
								price_yes = Price.objects.create(option=option, is_yes=True, is_last=True)
								price_no = Price.objects.create(option=option, is_yes=False, is_last=True)

						return redirect('/market/?marketId=' + str(market.pk))

					except IntegrityError:
						return redirect('/market/?marketId=' + str(market.pk))

	else:
		market_form = CreateMarketForm(user=request.user, group=group)
		option_formset = OptionFormSet()

	args = {'form': market_form, 'option_formset': option_formset}
	return render(request, 'market/create_market.html', args)


@login_required()
def edit_market_view(request):
	market_id = request.GET.get('marketId')
	market = get_object_or_404(Market, pk=market_id)
	user = request.user
	if not market.creator == user:
		raise PermissionDenied(_("You can't edit this market."))

	if request.method == "POST":
		if request.POST.get('delete') is not None:
			group = market.group
			market.delete()
			if group:
				return redirect('/group/?groupId=' + str(group.pk))
			else:
				return redirect('/')

		market_form = EditMarketForm(request.POST, request.FILES, instance=market)

		if market_form.is_valid():
			market = market_form.save()

			return redirect('/market/?marketId=' + str(market.pk))
	else:
		market_form = EditMarketForm(instance=market)

	args = {'form': market_form}
	return render(request, 'market/edit_market.html', args)


@login_required()
def request_to_join_group(request):
	user = request.user
	group_id = request.GET.get('groupId')
	group = Group.objects.get(pk=group_id)
	try:
		joined_group = JoinedGroup.objects.get(user=user, group=group)
	except:
		joined_group = None

	if joined_group:
		raise PermissionDenied(_("You are already member of this group"))

	if request.method == "POST":
		form = MakeRequestToJoinForm(request.POST, user=user, group=group)
		if form.is_valid():
			form.save()

			return redirect('list_all_groups')
	else:
		form = MakeRequestToJoinForm(user=user, group=group)

	args = {'form': form, 'group': group}
	return render(request, 'group/create_request_join.html', args)


@login_required()
def accept_user_to_group_view(request):
	joined_group_id = request.GET.get('joinedGroupId')
	joined_group = get_object_or_404(JoinedGroup, pk=joined_group_id)
	if not joined_group.group.moderator == request.user:
		raise PermissionDenied(_("Only moderatos can access this page."))

	try:
		joined_group.is_accepted = True
		joined_group.joined_date = datetime.datetime.now()
		joined_group.save()
		return redirect('/group/members/?groupId=' + str(joined_group.group.pk))
	except:
		raise PermissionDenied(_("Only moderatos can access this page."))


@login_required()
def reject_user_to_group_view(request):
	joined_group_id = request.GET.get('joinedGroupId')
	joined_group = get_object_or_404(JoinedGroup, pk=joined_group_id)
	if not joined_group.group.moderator == request.user:
		raise PermissionDenied(_("Only moderatos can access this page."))

	try:
		group_id = str(joined_group.group.pk)
		joined_group.delete()
		return redirect('/group/members/?groupId=' + group_id)
	except:
		raise PermissionDenied(_("Only moderatos can access this page."))


@login_required()
def list_members_group_view(request):
	group_id = request.GET.get('groupId')
	group = get_object_or_404(Group, pk=group_id)
	if not group.moderator == request.user:
		raise PermissionDenied(_("Only moderators can access this page."))
	joined_groups = group.joinedgroup_set.all()
	page = request.GET.get('page')
	paginator = Paginator(joined_groups, per_page=10)

	try:
		joined_groups = paginator.get_page(page)
	except PageNotAnInteger:
		joined_groups = paginator.get_page(1)
	except EmptyPage:
		joined_groups = paginator.page(paginator.num_pages)

	args = {'joined_groups': joined_groups, 'view_name': 'member_list', 'group_id': group_id}

	return render(request, 'group/list_members.html', args)


def display_profile_view(request):
	user_profile_id = request.GET.get('userId')
	user_profile = get_object_or_404(User, pk=user_profile_id)

	args = {'user_profile': user_profile}

	return render(request, 'user/display_user.html', args)


@login_required()
def cancel_deletion_user_view(request):
	user = request.user
	user.deletion_date = None
	user.save()

	args = {'user_profile': user}

	return render(request, 'user/display_user.html', args)


def display_market_view(request):
	market_id = request.GET.get('marketId')
	market = get_object_or_404(Market, pk=market_id)
	group = market.group

	if group and (not group.is_visible and (not request.user in group.user_accepted_set())):
		raise PermissionDenied(_("The market is part of a private group in which you do not have access."))

	assets_number = Asset.objects.filter(market=market).count()

	asset_form = CreateAssetForm(user=request.user, market=market)
	args = {'market': market, 'assets_number': assets_number, 'asset_form': asset_form}

	return render(request, 'market/display_market.html', args)


def ajax_related_markets(request):
	market_id = request.GET.get('marketId', None)
	market = get_object_or_404(Market, pk=market_id)

	categories = market.categories.all()
	q = Q()

	if market.group:
		if categories:
			for category in categories.all():
				q |= (Q(is_judged=False) & Q(categories=category) & (Q(group=None) | Q(group=market.group)))
		else:
			q |= (Q(is_judged=False) & (Q(group=None) | Q(group=market.group)))
	else:
		if categories:
			for category in categories.all():
				q |= (Q(is_judged=False) & Q(categories=category) & Q(group=None))
		else:
			q |= (Q(is_judged=False) & Q(group=None))
	q &= (~Q(id=market_id))
	related_markets = Market.objects.filter(q).distinct()

	related_markets_list = []

	for market in related_markets:
		json_dummy = {
			'id': market.pk,
			'title': market.title,
			'picture': market.picture,
		}
		related_markets_list.append(json_dummy)

	data = json.dumps(related_markets_list)
	res = JsonResponse(data, safe=False)

	return res


def ajax_charts(request):
	market_id = request.GET.get('marketId', None)
	market = get_object_or_404(Market, pk=market_id)

	#  First, we must get the days of the duration of the market.
	if get_language() == "es":
		date_format = "%d/%m/%Y"
	else:
		date_format = "%Y-%m-%d"

	if market.has_expired:
		end = market.end_date
	else:
		end = datetime.date.today()
	start = market.creation_date
	delta = end - start

	days = [(start + datetime.timedelta(days=x)) for x in range(delta.days + 1)]

	#  Then, we can get the labels for the x axis (labels).
	labels = [x.strftime(date_format) for x in days]

	options = []
	if market.is_binary:
		q0 = Q()
	else:
		q0 = Q(is_yes=True)

	for option in market.option_set.all():
		#  After that, we get the data for the y axis.
		q = q0 & Q(option=option)
		price_per_day = Price.objects.filter(q).order_by('date').values_list('buy_price', flat=True)
		options_json = {
			'name': option.name,
			'values': list(price_per_day),
			'binary_yes': option.binary_yes
		}
		options.append(options_json)

	json_dummy = {
		'labels': labels,
		'options': options
	}

	data = json.dumps(json_dummy)
	return JsonResponse(data, safe=False)


@login_required()
def buy_asset_view(request):
	user = request.user
	market_id = request.GET.get('marketId')
	market = get_object_or_404(Market, pk=market_id)
	group = market.group

	if group and (not group.is_visible and (not request.user in group.user_accepted_set())):
		raise PermissionDenied(_("The market is part of a private group in which you do not have access."))

	if request.method == "POST":
		form = CreateAssetForm(request.POST, user=user, market=market)
		if form.is_valid():
			option_id = request.POST.get('optionId')
			option = get_object_or_404(Option, pk=option_id)
			is_yes = request.POST.get('is_yes')

			asset = form.save(commit=False)
			asset.option = option
			if is_yes:
				asset.is_yes = True
			else:
				asset.is_yes = False

			asset.save()

			return redirect('/market/?marketId=' + str(market_id))
	else:
		return redirect('/market/?marketId=' + str(market_id))


def list_markets_view(request):
	user = request.user
	user_verified = False
	query_public_groups = Q(group=None)
	query_private_groups = Q()
	if user.is_authenticated:
		groups_ids = JoinedGroup.objects.filter(user=user, is_accepted=True).values_list('group_id', flat=True)
		query_private_groups = Q(group__in=groups_ids)
		user_verified = user.is_verified

	query_public_groups |= query_private_groups
	all_markets = Market.objects.filter(Q(is_judged=False) & query_public_groups).order_by('end_date')

	paginator = Paginator(all_markets, per_page=10)
	page = request.GET.get('page')

	try:
		markets = paginator.get_page(page)
	except PageNotAnInteger:
		markets = paginator.get_page(1)
	except EmptyPage:
		markets = paginator.page(paginator.num_pages)

	args = {'markets': markets, 'user_verified': user_verified}

	return render(request, 'market/list_markets.html', args)