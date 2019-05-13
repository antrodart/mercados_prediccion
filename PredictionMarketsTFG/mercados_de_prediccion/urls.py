from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
	path('contact/', views.ContactView.as_view(), name='contact'),

	path('categories/', views.list_categories_view, name='categories'),
	path('category/create/', views.create_category_view, name='create_category'),
	path('category/edit/', views.edit_category_view, name='edit_category'),

	path('groups/created/', views.list_created_groups_view, name='list_created_groups'),
	path('group/create/', views.create_group_view, name='create_group'),
	path('group/edit/', views.edit_group_view, name='edit_group'),
	path('group/', views.display_group_view, name='display_group'),
]