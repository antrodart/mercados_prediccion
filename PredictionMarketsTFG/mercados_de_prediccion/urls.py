from django.urls import path
from . import views, charts

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
	path('contact/', views.ContactView.as_view(), name='contact'),
	path('user/', views.display_profile_view, name='display_profile'),
	path('user/cancel-deletion', views.cancel_deletion_user_view, name='cancel_deletion_user'),

	path('categories/', views.list_categories_view, name='categories'),
	path('category/create/', views.create_category_view, name='create_category'),
	path('category/edit/', views.edit_category_view, name='edit_category'),

	path('groups/all/', views.list_all_groups_view, name='list_all_groups'),
	path('groups/created/', views.list_created_groups_view, name='list_created_groups'),
	path('group/create/', views.create_group_view, name='create_group'),
	path('group/edit/', views.edit_group_view, name='edit_group'),
	path('group/', views.display_group_view, name='display_group'),
	path('group/request-join/', views.request_to_join_group, name='request_to_join_group'),
	path('group/accept/', views.accept_user_to_group_view, name='accept_user_to_group'),
	path('group/members/', views.list_members_group_view, name='list_members_group'),

	path('market/create/', views.create_market_view, name='create_market'),
	path('market/edit/', views.edit_market_view, name='edit_market'),
	path('market/', views.display_market_view, name='display_market'),

	path('asset/buy/', views.buy_asset_view, name='buy_asset'),

	path('ajax/related_markets/', views.ajax_related_markets, name='related_markets'),
	path('ajax/chart/', views.line_chart_json, name='line_chart_json'),

]