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
from .utils import *
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
	paginator = Paginator(all_categories, per_page=12)
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
def list_created_communities_view(request):
	created_communities = Community.objects.filter(moderator=request.user.id).order_by('creation_date')
	paginator = Paginator(created_communities, per_page=12)
	page = request.GET.get('page')

	try:
		communities = paginator.get_page(page)
	except PageNotAnInteger:
		communities = paginator.get_page(1)
	except EmptyPage:
		communities = paginator.page(paginator.num_pages)

	args = {'communities': communities, 'view_name': 'list_created'}

	return render(request, 'community/list_communities.html', args)


def list_all_communities_view(request):
	all_communities = Community.objects.filter(is_visible=True).order_by('creation_date')
	paginator = Paginator(all_communities, per_page=12)
	page = request.GET.get('page')

	try:
		communities = paginator.get_page(page)
	except PageNotAnInteger:
		communities = paginator.get_page(1)
	except EmptyPage:
		communities = paginator.page(paginator.num_pages)

	args = {'communities': communities, 'view_name': 'list_all'}

	return render(request, 'community/list_communities.html', args)


@login_required()
def create_community_view(request):
	if request.method == "POST":
		form = CreateCommunityForm(request.POST, request.FILES, user=request.user)
		if form.is_valid():
			community = form.save(commit=False)
			is_visible = request.POST.get('is_visible')
			if is_visible:
				community.is_visible = True
			else:
				community.is_visible = False

			community.save()

			joined_community = JoinedCommunity(is_accepted=True, user=request.user, community_id=community.pk)
			joined_community.save()

			return redirect('/community/?communityId=' + str(community.pk))
	else:
		form = CreateCommunityForm(user=request.user)

	args = {'form': form}
	return render(request, 'community/create_community.html', args)


@login_required()
def edit_community_view(request):
	community_id = request.GET.get('communityId')
	community = get_object_or_404(Community, pk=community_id)
	if not community.moderator == request.user:
		raise PermissionDenied(_("You cannot edit this community."))
	if request.method == "POST":
		if request.POST.get('delete') is not None:
			community.delete()
			return redirect('/communities/created')

		form = CreateCommunityForm(request.POST, request.FILES, instance=community, user=request.user)
		if form.is_valid():
			community = form.save(commit=False)
			is_visible = request.POST.get('is_visible')
			if is_visible:
				community.is_visible = True
			else:
				community.is_visible = False

			community.save()

			return redirect('/community/?communityId=' + str(community_id))
	else:
		form = CreateCommunityForm(instance=community, user=request.user)

	args = {'form': form, 'editing': True}
	return render(request, 'community/create_community.html', args)


@login_required()
def display_community_view(request):
	community_id = request.GET.get('communityId')
	user = request.user
	community = get_object_or_404(Community, pk=community_id)
	try:
		joined_community = JoinedCommunity.objects.get(user=user, community=community)
	except:
		joined_community = None

	user_has_requested = False
	user_is_accepted = False
	if joined_community:
		user_has_requested = True
		user_is_accepted = joined_community.is_accepted


	args = {'community': community, 'user_has_requested': user_has_requested, 'user_is_accepted': user_is_accepted}

	return render(request, 'community/display_community.html', args)


@login_required()
def create_market_view(request):
	user = User.objects.get(pk=request.user.pk)
	community_id = request.GET.get('communityId')
	if community_id:
		community = get_object_or_404(Community, pk=community_id)
	else:
		community = None

	if community and not community.moderator == user:
		raise PermissionDenied(_("You can't create a market in this community."))
	elif not community and not user.is_staff and not user.is_verified:
		raise PermissionDenied(_("You can't create a public market. Please contact us if you want to verify your account and create public markets."))

	# Create the formset, specifying the form and formset we want to use.
	OptionFormSet = formset_factory(CreateOptionForm, formset=BaseOptionFormSet, min_num=2,max_num=10)

	if request.method == "POST":
		market_form = CreateMarketForm(request.POST, request.FILES, user=request.user, community=community)
		option_formset = OptionFormSet(request.POST)

		if market_form.is_valid():
			if market_form.cleaned_data['market_type'] == '1':  #  The market is binary
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
							if market.is_exclusive:
								num_options = len(new_options)
								for option in new_options:
									option.save()
									price_yes = Price.objects.create(option=option, is_yes=True, is_last=True, buy_price=round(100/num_options))
							else:
								for option in new_options:
									option.save()
									price_yes = Price.objects.create(option=option, is_yes=True, is_last=True)
									price_no = Price.objects.create(option=option, is_yes=False, is_last=True)

						return redirect('/market/?marketId=' + str(market.pk))

					except IntegrityError:
						return redirect('/market/?marketId=' + str(market.pk))

	else:
		market_form = CreateMarketForm(user=request.user, community=community)
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
			community = market.community
			market.delete()
			if community:
				return redirect('/community/?communityId=' + str(community.pk))
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
def request_to_join_community(request):
	user = request.user
	community_id = request.GET.get('communityId')
	community = Community.objects.get(pk=community_id)
	try:
		joined_community = JoinedCommunity.objects.get(user=user, community=community)
	except:
		joined_community = None

	if joined_community:
		raise PermissionDenied(_("You are already member of this community."))

	if request.method == "POST":
		form = MakeRequestToJoinForm(request.POST, user=user, community=community)
		if form.is_valid():
			form.save()

			return redirect('list_all_communities')
	else:
		form = MakeRequestToJoinForm(user=user, community=community)

	args = {'form': form, 'community': community}
	return render(request, 'community/create_request_join.html', args)


@login_required()
def accept_user_to_community_view(request):
	joined_community_id = request.GET.get('joinedCommunityId')
	joined_community = get_object_or_404(JoinedCommunity, pk=joined_community_id)
	if not joined_community.community.moderator == request.user:
		raise PermissionDenied(_("Only moderatos can access this page."))

	try:
		joined_community.is_accepted = True
		joined_community.joined_date = datetime.datetime.now()
		joined_community.save()
		return redirect('/community/members/?communityId=' + str(joined_community.community.pk))
	except:
		raise PermissionDenied(_("Only moderatos can access this page."))


@login_required()
def reject_user_to_community_view(request):
	joined_community_id = request.GET.get('joinedCommunityId')
	joined_community = get_object_or_404(JoinedCommunity, pk=joined_community_id)
	if not joined_community.community.moderator == request.user:
		raise PermissionDenied(_("Only moderatos can access this page."))

	try:
		community_id = str(joined_community.community.pk)
		joined_community.delete()
		return redirect('/community/members/?communityId=' + community_id)
	except:
		raise PermissionDenied(_("Only moderatos can access this page."))


@login_required()
def list_members_community_view(request):
	community_id = request.GET.get('communityId')
	community = get_object_or_404(Community, pk=community_id)
	if not community.moderator == request.user:
		raise PermissionDenied(_("Only moderators can access this page."))
	joined_communities = community.joinedcommunity_set.all()
	page = request.GET.get('page')
	paginator = Paginator(joined_communities, per_page=10)

	try:
		joined_communities = paginator.get_page(page)
	except PageNotAnInteger:
		joined_communities = paginator.get_page(1)
	except EmptyPage:
		joined_communities = paginator.page(paginator.num_pages)

	args = {'joined_communities': joined_communities, 'view_name': 'member_list', 'community_id': community_id}

	return render(request, 'community/list_members.html', args)


def display_profile_view(request):
	user_profile_id = request.GET.get('userId')
	user_profile = get_object_or_404(User, pk=user_profile_id)

	created_communities = Community.objects.filter(moderator=request.user.pk)
	assets = Asset.objects.filter(user=request.user.pk, market__is_judged=False)

	args = {'user_profile': user_profile, 'created_communities': created_communities, 'assets': assets}

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
	community = market.community

	check_user_is_member_of_community(user=request.user, community=community)
	assets_number = Asset.objects.filter(market=market).aggregate(Sum('quantity'))['quantity__sum']
	if market.has_expired:

		args = {'market': market, 'assets_number': assets_number}

		return render(request, 'market/display_market_ended.html', args)
	else:
		if community:
			user_karma = JoinedCommunity.objects.get(community=community, user=request.user).private_karma
		else:
			user_karma = request.user.public_karma

		asset_form = CreateAssetForm(user=request.user, market=market)
		args = {'market': market, 'assets_number': assets_number, 'asset_form': asset_form, 'user_karma': user_karma}

		return render(request, 'market/display_market.html', args)


def ajax_related_markets(request):
	market_id = request.GET.get('marketId', None)
	market = get_object_or_404(Market, pk=market_id)

	categories = market.categories.all()
	q = Q()

	if market.community:
		if categories:
			for category in categories.all():
				q |= (Q(is_judged=False) & Q(categories=category) & (Q(community=None) | Q(community=market.community)))
		else:
			q |= (Q(is_judged=False) & (Q(community=None) | Q(community=market.community)))
	else:
		if categories:
			for category in categories.all():
				q |= (Q(is_judged=False) & Q(categories=category) & Q(community=None))
		else:
			q |= (Q(is_judged=False) & Q(community=None))
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
	community = market.community

	check_market_has_not_expired(market)
	check_user_is_member_of_community(user=user, community=community)

	if request.method == "POST":
		form = CreateAssetForm(request.POST, user=user, market=market)
		if form.is_valid():
			option_id = request.POST.get('optionId')
			option = get_object_or_404(Option, pk=option_id)
			is_yes = request.POST.get('is_yes')

			with transaction.atomic():
				asset = form.save(commit=False)
				asset.option = option
				if is_yes:
					asset.is_yes = True
				else:
					asset.is_yes = False

				user_subtract_karma(user, asset, community, market)
				if market.is_binary or not market.is_exclusive:
					recalculate_price_binary_options(option, asset)
				else:
					recalculate_price_exclusive_options(market=market, option=option, asset=asset)

			return redirect('/market/?marketId=' + str(market_id))


def list_markets_view(request):
	user = request.user
	category_id = request.GET.get('categoryId')
	if category_id:
		category = Category.objects.get(pk=category_id)
		q_category = Q(categories__in=category_id)
	else:
		category = None
		q_category = Q()

	user_verified = False
	q_public_communities = Q(community=None)
	q_private_communities = Q()
	if user.is_authenticated:
		communities_ids = JoinedCommunity.objects.filter(user=user, is_accepted=True).values_list('community_id', flat=True)
		q_private_communities = Q(community__in=communities_ids)
		user_verified = user.is_verified

	q_public_communities |= q_private_communities
	all_markets = Market.objects.filter(q_public_communities & q_category).order_by('is_judged', 'end_date')

	paginator = Paginator(all_markets, per_page=9)
	page = request.GET.get('page')

	try:
		markets = paginator.get_page(page)
	except PageNotAnInteger:
		markets = paginator.get_page(1)
	except EmptyPage:
		markets = paginator.page(paginator.num_pages)

	args = {'markets': markets, 'user_verified': user_verified, 'category': category}

	return render(request, 'market/list_markets.html', args)


def list_judge_public_markets(request, created=False):
	if not request.user.is_staff:
		raise PermissionDenied(_("Must be logged as Admin."))

	q = Q(community=None, is_judged=False, end_date__lt=datetime.date.today())
	if created:
		q &= Q(creator=request.user)

	markets_to_judge = Market.objects.filter(q)
	paginator = Paginator(markets_to_judge, per_page=9)
	page = request.GET.get('page')

	try:
		markets = paginator.get_page(page)
	except PageNotAnInteger:
		markets = paginator.get_page(1)
	except EmptyPage:
		markets = paginator.page(paginator.num_pages)

	args = {'markets': markets, 'created': created}

	return render(request, 'market/list_judge_markets.html', args)


def judge_market(request, market_id, slug):
	market = get_object_or_404(Market, pk=market_id)
	user = request.user
	creator = market.creator

	if not market.has_expired:
		raise ObjectDoesNotExist(_("The market does not exist or it has not expired"))

	if market.community is None:  #  Market is public, only moderators and is creator if he is verified can judge
		if creator.is_verified and not user == creator:
			raise PermissionDenied(_("Must be the market creator."))
		elif creator.is_staff and not user.is_staff:
			raise PermissionDenied(_("Must be logged as Admin."))
	else:  #  Market is not public, only the creator of the market can judge it (the community moderator)
		if not user == creator:
			raise PermissionDenied(_("Must be the creator of the Market"))

	if request.method == "POST":
		if market.is_binary:
			options = market.option_set.values_list('id', flat=True)
			if get_language() == "es":
				option_choices = [(options[0], "Sí"), (options[1], "No")]
			else:
				option_choices = [(options[0], "Yes"), (options[1], "No")]

			form = JudgeBinaryMarketForm(request.POST, option_choices=option_choices)
			if form.is_valid():
				correct_option_id = form.cleaned_data.get('options')
				correct_option = get_object_or_404(Option, pk=correct_option_id)
				if not int(correct_option_id) in options:
					raise PermissionDenied(_("The option is not from this market."))

				with transaction.atomic():
					market.is_judged = True
					market.save()
					correct_option.is_correct = True
					correct_option.save()
					pay_winner_option(option=correct_option, non_exclusive_market=False, is_yes=None)

				return redirect("/market/?marketId=" + str(market.pk))

		elif market.is_exclusive:
			options = market.option_set.values_list('id', 'name')
			form = JudgeBinaryMarketForm(request.POST, option_choices=options)
			if form.is_valid():
				correct_option_id = form.cleaned_data.get('options')
				correct_option = get_object_or_404(Option, pk=correct_option_id)
				if not correct_option in market.option_set.all():
					raise PermissionDenied(_("The option is not from this market."))

				with transaction.atomic():
					market.is_judged = True
					market.save()
					correct_option.is_correct = True
					correct_option.save()
					pay_winner_option(option=correct_option, non_exclusive_market=False, is_yes=None)

				return redirect("/market/?marketId=" + str(market.pk))
		else:
			options = market.option_set.values_list('id', 'name')
			form = JudgeMultipleNonExclusiveMarketForm(request.POST, option_choices=options)
			if form.is_valid():
				correct_options_ids = form.cleaned_data.get('options')
				try:
					with transaction.atomic():
						market.is_judged = True
						market.save()
						correct_options = market.option_set.filter(pk__in=correct_options_ids)
						incorrect_options = market.option_set.exclude(pk__in=correct_options_ids)
						for correct_option in correct_options:
							correct_option.is_correct = True
							correct_option.save()
							pay_winner_option(option=correct_option, non_exclusive_market=True, is_yes=True)
						for incorrect_option in incorrect_options:
							pay_winner_option(option=incorrect_option, non_exclusive_market=True, is_yes=False)
				except:
					raise PermissionDenied()
				return redirect("/market/?marketId=" + str(market.pk))

	else:
		if market.is_binary:
			options = market.option_set.values_list('id', flat=True)
			if get_language() == "es":
				option_choices = [(options[0], "Sí"),(options[1], "No")]
			else:
				option_choices = [(options[0], "Yes"),(options[1], "No")]

			form = JudgeBinaryMarketForm(option_choices=option_choices)
		elif market.is_exclusive:
			options = market.option_set.values_list('id', 'name')
			form = JudgeBinaryMarketForm(option_choices=options)
		else:
			options = market.option_set.values_list('id', 'name')
			form = JudgeMultipleNonExclusiveMarketForm(option_choices=options)

	args = {'form': form, 'market': market}
	return render(request, 'market/judge_market.html', args)


def past_bets(request, user_id):
	user = get_object_or_404(User, pk=user_id)

	if not request.user.is_authenticated:
		communities = None
		markets = Market.objects.filter(is_judged=True, community__isnull=True)
	elif request.user.pk == user.pk:
		communities = Community.objects.filter(joinedcommunity__user_id=user.pk, joinedcommunity__is_accepted=True)
		if communities:
			markets = Market.objects.filter(is_judged=True, community__in=communities) | Market.objects.filter(
				is_judged=True, community__isnull=True)
		else:
			markets = Market.objects.filter(is_judged=True, community__isnull=True)
	else:
		user_logged = request.user
		user_logged_communities = Community.objects.filter(joinedcommunity__user_id=user_logged.pk,
		                                                   joinedcommunity__is_accepted=True)
		user_communities = Community.objects.filter(joinedcommunity__user_id=user.pk, joinedcommunity__is_accepted=True)
		communities = user_logged_communities & user_communities
		if communities:
			markets = Market.objects.filter(is_judged=True, community__in=communities) | Market.objects.filter(
				is_judged=True, community__isnull=True)
		else:
			markets = Market.objects.filter(is_judged=True, community__isnull=True)


	assets = Asset.objects.filter(user=user, market__in=markets)

	args = {'assets': assets, 'user_past_bets': user, 'communities': communities}

	return render(request, 'statistics/past_bets.html', args)

