from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_text
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from .models import Category
from .forms import *
import base64



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
		raise PermissionDenied("Must be logged as Admin.")
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
		raise PermissionDenied("Must be logged as Admin.")
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
def create_group_view(request):
	if request.method == "POST":
		form = CreateGroupForm(request.POST, request.FILES, user=request.user)
		if form.is_valid():
			form.save()

			return redirect('home')
	else:
		form = CreateGroupForm(user=request.user)

	args = {'form': form}
	return render(request, 'group/create_group.html', args)