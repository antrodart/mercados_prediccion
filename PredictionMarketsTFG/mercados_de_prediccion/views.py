from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from .forms import *
from users.models import User



class HomePageView(TemplateView):
	template_name = 'home.html'


class AboutView(TemplateView):
	template_name = 'about.html'


class ContactView(TemplateView):
	template_name = 'contact.html'


def list_categories_view(request):
	all_categories = Category.objects.all()
	paginator = Paginator(all_categories, per_page=10)
	page = request.GET.get('page')

	try:
		categories = paginator.get_page(page)
	except PageNotAnInteger:
		categories = paginator.get_page(1)
	except EmptyPage:
		categories = paginator.page(paginator.num_pages)

	args = {'categories': categories}

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

	args = {'groups': groups, 'view_name':'list_created'}

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

	args = {'groups': groups, 'view_name':'list_all'}

	return render(request, 'group/list_groups.html', args)


@login_required()
def create_group_view(request):
	if request.method == "POST":
		form = CreateGroupForm(request.POST, request.FILES, user=request.user)
		if form.is_valid():
			form.save()

			return redirect('list_created_groups')
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
		form = CreateGroupForm(request.POST, request.FILES, instance=group, user=request.user)
		if form.is_valid():
			form.save()

			return redirect('list_created_groups')
	else:
		form = CreateGroupForm(instance=group, user=request.user)

	args = {'form': form, 'editing':True}
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

	args = {'group': group, 'user_is_member':user_is_member}

	return render(request, 'group/display_group.html', args)


@login_required()
def create_market_view(request):
	group_id = request.GET.get('groupId')
	group = Group.objects.get(pk=group_id)
	user = request.user
	if group and (not group.moderator == user):
		raise PermissionDenied(_("You can't create a market in this group."))
	if request.method == "POST":
		form = CreateMarketForm(request.POST, request.FILES, user=request.user, group=group)
		if form.is_valid():
			form.save()

			return redirect('list_created_groups')
	else:
		form = CreateMarketForm(user=request.user, group=group)

	args = {'form': form}
	return render(request, 'market/create_market.html', args)


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
		return redirect('/group/members/?groupId='+str(joined_group.group.pk))
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
		return redirect('/group/members/?groupId='+group_id)
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

	args = {'joined_groups': joined_groups, 'view_name': 'member_list', 'group_id':group_id}

	return render(request, 'group/list_members.html', args)


def display_profile_view(request):
	user_profile_id = request.GET.get('userId')
	user_profile = get_object_or_404(User, pk=user_profile_id)

	args = {'user_profile': user_profile}

	return render(request, 'user/display_user.html', args)
